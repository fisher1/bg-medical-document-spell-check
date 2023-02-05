# bg-medical-document-spell-check
#### CC-BY-SA cite as:
G. Svilen, "Automatic Spelling Correction for Medical Texts in Bulgarian language", 2023, Sofia University “St. Kliment Ohridski”, Faculty of Mathematics and Informatics

#### Abstract
There exists a large volume of medical texts in Bulgarian language, but due to the nature of these texts, the existing standard spell checkers for common vocabulary don’t perform well for specialized medical terms and abbreviations. The goal of this thesis is to create a spell checker and spell correction service designed for medical texts in Bulgarian language.

For the purposes of this thesis, a corpus of anonymized clinical data is used – sentences from patient history data and samples from clinical statuses. Dictionaries with medical terms for anatomical organs and systems of the human body, symptoms of diseases, as well as a standard dictionary of the Bulgarian language are also used.

An extended vocabulary and lists of bigrams and collocations are compiled from the corpus of clinical data, using the dictionaries.

Spell checking is performed by searching each word of the text in the dictionary. If the word is missing from the dictionary, it is assumed to be probably misspelled and a list of suggestions for its correction should be created.

Approaches based on calculating distances between words are used to create spelling correction suggestions. For each word to be corrected, the preceding word is also examined to look for a correct spelling in the list of collocations. The search for similar words in the dictionary is performed, first by a Jaccard distance with a set maximum threshold to remove too dissimilar words, and then by a Levenshtein distance to order the sentences by similarity to the corrected word.

Using these methods, a spell checking and correction service has been developed that provides a user interface with automatic spell checking as well as a programming API that can be integrated with existing text editing software applications.
