# import the modules
import json
import pickle
from flask import Flask, request, jsonify, after_this_request
import tweepy
import re
import bz2

# assign the keys accordingly
consumer_key = "FTEg6C5YxG7pLvXW0hEJBELod"
consumer_secret = "h8rkwNmGsZdhu0x5X51oBQ4Ff0xo9jsEtaDLiLapfL4f1q2ciN"
access_token = "1453142856-Ino0V6ZfaqKCeBtQOUqMXqN9ScFhnfzQTSBDDk4"
access_token_secret = "Xoflw1ecWha0G22XlUA5KhhBFEVAxbTX1WXExEUYc18HI"


# decompress the saved model
def decompress_model():
    with bz2.BZ2File('newrfcmodel.pkl.bz2', 'rb') as f:
        decompressed_data = f.read()
        file = pickle.loads(decompressed_data)
        return file


# ps = PorterStemmer()
app = Flask(__name__)
# loading the saved model and the vectorizer
tfidf = pickle.load(open('newrfcvectorizer.pkl', 'rb'))
model = decompress_model()


def extract_text(tweet):
    tweet = re.sub(r',(\d)', r'\1', tweet)
    tweet = re.sub("@[A-Za-z0-9_]+", "", tweet)
    tweet = re.sub(r'http\S+', '', tweet)
    tweet = remove_emojis(tweet).lower()
    return tweet


def remove_symbols(text: str) -> str:
    # use regular expression to remove all symbols
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text


# Check if the tweet text is fully english
def is_english_text(text):
    try:
        text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001f600-\U0001f64f"  # emoticons
                               u"\U0001f300-\U0001f5ff"  # symbols & pictographs
                               u"\U0001f680-\U0001f6ff"  # transport & map symbols
                               u"\U0001f1e0-\U0001f1ff"  # flags (iOS)
                               u"\U00002702-\U000027b0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs (Unicode 13.0)
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r' ', text)


def get_tweet(tweet_id):
    # authorization of consumer key and consumer secret
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
    # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # set access to user's access key and access secret
    auth.set_access_token(access_token, access_token_secret)

    # calling the api
    api = tweepy.API(auth)

    # fetching the status
    status = api.get_status(tweet_id, tweet_mode='extended')
    # fetching the text attribute
    text = status.full_text
    if is_english_text(text):
        cleaned_tweet = extract_text(text)
        return cleaned_tweet
    else:
        return text


@app.route('/')
def main_page():
    return "Server is running!"


@app.route('/predict', methods=["POST"])
def predict():
    data = json.loads(request.data)
    values = data['Tweet_ID']
    # 1. get Tweet text
    tweet = get_tweet(values)

    @after_this_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    # Check if tweet text is empty or not
    if len(tweet) != 0:
        # Check if the tweet text is english or not
        if is_english_text(remove_symbols(tweet)):
            tweet = extract_text(tweet)
            # Check the extracted text from the tweet
            if (len(remove_symbols(tweet)) > 0) and (remove_symbols(tweet).isspace() == False):
                # 2. vectorizer
                vector_input = tfidf.transform([remove_symbols(tweet)])
                # 3. check
                result = model.predict(vector_input)[0]
                # Get class probability
                probability = model.predict_proba(vector_input)
                # 4. Display
                if result == 1:
                    # Probability of not being a scam
                    non_scam_probability = probability[0][1]
                    message = {'message': "Not a Scam",
                               'percentage': "{:.0f}".format(non_scam_probability * 100), 'type': "nscam"}
                    return jsonify(message)
                else:
                    # Probability of being a scam
                    scam_probability = probability[0][0]
                    message = {'message': "Potential Scam",
                               'percentage': "{:.0f}".format(scam_probability * 100), 'type': "scam"}
                    return jsonify(message)
            else:
                message = {'message': "Tweet does not contain any text", 'percentage': "0"}
                return jsonify(message)
        else:
            message = {'message': "The text in the tweet is not entirely in English", 'percentage': "0"}
            return jsonify(message)

    else:
        message = {'message': "Tweet does not contain any text", 'percentage': "0"}
        return jsonify(message)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
