import heapq
import itertools
from flask import Flask, request, current_app
from flask_cors import CORS, cross_origin
from nltk.metrics.distance import edit_distance, jaccard_distance
import pandas as pd

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

NUMBER_OF_SUGGESTIONS = 5

unigrams = pd.read_csv('../final_training_data/correct.csv')
collocations = pd.read_csv('../final_training_data/collocations_new.csv')
bigrams = pd.read_csv('../final_training_data/bigrams_new.csv')
dictionary = pd.read_csv('dictionary_2.csv')

unigram_buckets = {}
for _, unigram in unigrams.iterrows():
    word = unigram['Word']
    count = unigram['Count']

    for i in range(0, len(word)):
        word_cut = word[0:i]
        if word_cut not in unigram_buckets:
            unigram_buckets[word_cut] = []
        if len(unigram_buckets[word_cut]) < 10:
            unigram_buckets[word_cut].append([i-len(word), count, word])


def get_suggestions(curr_word, preceeding_word, num_suggestions):
    suggestions = [[-100, i, ''] for i in range(-num_suggestions, 0)]
    heapq.heapify(suggestions)
    
    # Collocations
    row = collocations.loc[collocations['First'] == preceeding_word]
    if not row.empty:
        row = row.iloc[0]
        distance = edit_distance(row['Second'], curr_word)
        if distance <= 3:
            heapq.heappushpop(suggestions, [0, 0, row['Second']])

    # Bigrams ??

    # Unigrams
    for _, unigram in unigrams.iterrows():
        if unigram['Word'] == curr_word or [0,0,unigram['Word']] in suggestions:
            continue
        distance = jaccard_distance(set(unigram['Word']), set(curr_word))
        if distance < 0.35 or (len(unigram['Word']) <= 3 and len(curr_word) <=3):
            edit_distance_curr = edit_distance(unigram['Word'], curr_word)
            heapq.heappushpop(suggestions, [-edit_distance_curr, unigram['Count'], unigram['Word']])

    # Unigrams autocompletion (unigram buckets)
    if curr_word in unigram_buckets:
        for word in unigram_buckets[curr_word]:
            if word not in suggestions:
                heapq.heappushpop(suggestions, word)

    # Dictionary ??

    end_list = []
    for _ in range(len(suggestions)):
        suggestion = heapq.heappop(suggestions)[2]
        if suggestion != '':
            end_list.append(suggestion)
    end_list.reverse()
    return end_list

def get_dash_word_suggestions(curr_word, curr_suggestions):
    words = curr_word.split('-')
    suggestions_for_word = {}
    for word in words:
        exists_in_dictionary = (unigrams['Word'] == word).any() or (dictionary["name"] == word).any()
        if not exists_in_dictionary:
            suggestions_for_word[word] = get_suggestions(word, None, NUMBER_OF_SUGGESTIONS)
        else:
            suggestions_for_word[word] = [word]

    suggestion_combinations = list(map(
        lambda x: '-'.join(x),
        itertools.product(*suggestions_for_word.values())
    ))

    for suggestion in curr_suggestions:
        if suggestion in suggestion_combinations:
            suggestion_combinations.remove(suggestion)

    len_combinations = len(suggestion_combinations)
    if not len_combinations:
        return []
    
    len_suggestions = min(len_combinations, NUMBER_OF_SUGGESTIONS - len(curr_suggestions))
    return suggestion_combinations[:len_suggestions]

@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return current_app.send_static_file('index.html')

@app.route('/suggestions', methods=['POST'])
def give_suggestions():
    data = request.json
    curr_word = data['currWord']
    preceeding_word = data['preceedingWord']

    return get_suggestions(curr_word, preceeding_word, NUMBER_OF_SUGGESTIONS)

@app.route('/correct', methods=['POST'])
def correct_text():
    split_text = []
    data = request.json
    text = data['text']
    suggestions = data['alreadyExtracted']
    tokens = text.split(' ')
    last_token = None
    for i in range(0, len(tokens)):
        if tokens[i] == '': continue

        next_token = None
        token = tokens[i]

        has_number = any(char.isdigit() for char in token)

        if has_number: last_token = None

        punctuation_mark = token[-1] if token[-1] in ['.', '?', '!', ','] else None
        if punctuation_mark: token = token[:-1]

        uppercase = False
        if not token.isupper() and token[0].isupper() and (len(token) == 1 or not token[1].isupper()):
            uppercase = True
            token = token.lower()
            
        if not punctuation_mark and i+1 < len(tokens): next_token=tokens[i+1]
        
        suggestion_key = (last_token or '') + '|del|' + token + '|del|' + (next_token or '')
        split_text.append({
            'word': token,
            'suggestion_key': suggestion_key,
            'punctuation_mark': punctuation_mark,
            'uppercase': uppercase,
        })
        
        exists_in_dictionary = (unigrams['Word'] == token).any() or (dictionary["name"] == token).any()
        is_special_character = token in ['-', ';', ':', '*']

        if not has_number and not exists_in_dictionary and not is_special_character and suggestion_key not in suggestions:
            curr_suggestions = get_suggestions(token, last_token, NUMBER_OF_SUGGESTIONS)
            suggestions[suggestion_key] = curr_suggestions
            if len(curr_suggestions) < NUMBER_OF_SUGGESTIONS and '-' in token:
                dash_suggestions = get_dash_word_suggestions(token, curr_suggestions)
                suggestions[suggestion_key] += dash_suggestions
        if not has_number: last_token = token

    return {
        'suggestions': suggestions,
        'split_text': split_text
    }

if __name__ == '__main__':
   app.run(debug=True)