import json
import openai  # Correct import
import os
import sqlite3
from time import time

print("Running db_bot.py!")

fdir = os.path.dirname(__file__)
def getPath(fname):
    return os.path.join(fdir, fname)

# SQLITE
sqliteDbPath = getPath("cr.db")
setupSqlPath = getPath("setup.sql")
setupSqlDataPath = getPath("setupData.sql")

sqliteCon = sqlite3.connect(sqliteDbPath) # create new db
sqliteCursor = sqliteCon.cursor()
with (
        open(setupSqlPath) as setupSqlFile,
        open(setupSqlDataPath) as setupSqlDataFile
    ):

    setupSqlScript = setupSqlFile.read()
    setupSQlDataScript = setupSqlDataFile.read()

def runSql(query):
    result = sqliteCursor.execute(query).fetchall()
    return result

# OPENAI
configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
    config = json.load(configFile)

openai.api_key = config["openaiKey"]  # Correct way to set the API key

def getChatGptResponse(content):

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Ensure you're using the correct model, such as gpt-4
        messages=[{"role": "user", "content": content}],
    )

    # Extract the response content directly from the API response
    try:
        result = response['choices'][0]['message']['content']
    except KeyError as e:
        result = f"Error accessing response content: {e}"

    return result


# strategies
commonSqlOnlyRequest = "Give me a sqlite select statement that answers the question. Only respond with sqlite syntax. If there is an error do not explain it!"
strategies = {
    "zero_shot": setupSqlScript + commonSqlOnlyRequest,
    
    "single_domain_double_shot": (setupSqlScript + 
                   " Which players have a deck that contains a Hog Rider? " + 
                   " \nSELECT p.player_name\nFROM Player p\nJOIN PlayerDeck pd ON p.player_id = pd.player_id\nJOIN DeckCard dc ON pd.deck_id = dc.deck_id\nJOIN Card c ON dc.card_id = c.card_id\nWHERE c.card_name = 'Hog Rider';\n " +
                   commonSqlOnlyRequest),
    
    "archetype_and_deck_cards": (setupSqlScript +
                   " Which players use a deck that includes both Valkyrie and Inferno Dragon? " +
                   "\nSELECT DISTINCT p.player_name\nFROM Player p\nJOIN PlayerDeck pd ON p.player_id = pd.player_id\nJOIN DeckCard dc ON pd.deck_id = dc.deck_id\nJOIN Card c ON dc.card_id = c.card_id\nWHERE c.card_name IN ('Valkyrie', 'Inferno Dragon')\nGROUP BY p.player_name\nHAVING COUNT(DISTINCT c.card_name) = 2;\n" +
                   commonSqlOnlyRequest),
    
    "deck_with_card_cost_above_6": (setupSqlScript +
                   " Who has a deck with a card that costs more than 6 elixir? " +
                   "\nSELECT DISTINCT p.player_name\nFROM Player p\nJOIN PlayerDeck pd ON p.player_id = pd.player_id\nJOIN DeckCard dc ON pd.deck_id = dc.deck_id\nJOIN Card c ON dc.card_id = c.card_id\nWHERE c.card_cost > 6;\n" +
                   commonSqlOnlyRequest)
}

questions = [
    "Which are the most popular Archetypes?",
    "Which players have multiple decks?",
    "Which cards are used in the most decks?",
    "Which players have a deck that contains a Hog Rider?",
    "Which Archetypes use the Balloon card?",
    "What are the namesof the players who use Log Bait decks?",
    "Which players have decks with a Lava Hound?",
    "Who has a deck with a card that costs more than 6 elixir?",
    "What cards are used in the highest number of decks in the database?",
    "Which players have a deck with a Rocket card?",
    "What is the most commonly used card type across all decks?"
]

def sanitizeForJustSql(value):
    gptStartSqlMarker = "```sql"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        value = value.split(gptStartSqlMarker)[1]
    if gptEndSqlMarker in value:
        value = value.split(gptEndSqlMarker)[0]

    return value

for strategy in strategies:
    responses = {"strategy": strategy, "prompt_prefix": strategies[strategy]}
    questionResults = []
    for question in questions:
        print(question)
        error = "None"
        sqlSyntaxResponse = ""  # Initialize it to an empty string here
        queryRawResponse = ""  # Also initialize the queryRawResponse here
        friendlyResponse = ""  # Initialize friendlyResponse here

        try:
            sqlSyntaxResponse = getChatGptResponse(strategies[strategy] + " " + question)
            sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)
            print(sqlSyntaxResponse)
            queryRawResponse = str(runSql(sqlSyntaxResponse))
            print(queryRawResponse)
            friendlyResultsPrompt = "I asked a question \"" + question +"\" and the response was \""+queryRawResponse+"\" Please, just give a concise response in a more friendly way? Please do not give any other suggests or chatter."
            friendlyResponse = getChatGptResponse(friendlyResultsPrompt)
            print(friendlyResponse)
        except Exception as err:
            error = str(err)
            print(err)

        questionResults.append({
            "question": question, 
            "sql": sqlSyntaxResponse, 
            "queryRawResponse": queryRawResponse,
            "friendlyResponse": friendlyResponse,
            "error": error
        })

    responses["questionResults"] = questionResults

    with open(getPath(f"response_{strategy}_{time()}.json"), "w") as outFile:
        json.dump(responses, outFile, indent = 2)
            

sqliteCursor.close()
sqliteCon.close()
print("Done!")
