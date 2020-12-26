import spacy
import neuralcoref


class QuestionGenerator:
    def __init__(self, input_article, quiz_count=0):
        # Load the language library
        self.nlp = spacy.load('en_core_web_md')
        # Coreference resolution
        neuralcoref.add_to_pipe(self.nlp)
        self.article = input_article
        self.resolved_sents = self.nlp(self.coref_resolution()).sents
        self.sentences = self.nlp(self.article).sents

    def coref_resolution(self):
        resolved_str = ''
        paragraphs = self.article.split('\n')
        for paragraph in paragraphs:
            unresolved_doc = self.nlp(paragraph)
            resolved_str += unresolved_doc._.coref_resolved + '\n'
        return resolved_str

    def generate_quiz(self, quiz_count, simple=False):
        self.quiz_count = quiz_count
        questions = []

        for sent in self.sentences:
            doc_unresolved = self.nlp(str(sent))
            pron_list = ['i','she','he','we','they']
            is_pron_in_subj = False
            is_pron_in_obj = False
            temp_is_pron_in_obj = False
            be_what_ques = True
            pron_count = 0
            pron_obj_count = 0
            for token in doc_unresolved[:sent.root.i]:
                if token.pos_ == 'PRON' and token.text.lower() in pron_list:
                    be_what_ques = False
                    if is_pron_in_subj == True:
                        pron_count += 1
                        break
                    is_pron_in_subj = True
                    temp_is_pron_in_obj = True
            for token in doc_unresolved[sent.root.i:-1]:
                if token.pos_ == 'PRON' and token.text.lower() in pron_list:
                    be_what_ques = False
                    if is_pron_in_obj == True:
                        pron_obj_count += 1
                        break
                    is_pron_in_subj = False
                    is_pron_in_obj = True
                    pron_obj_count += 1
            if is_pron_in_subj and pron_count == 0:
                try:
                    questions += self.who_question_subj(doc_unresolved)
                except:
                    pass
            if (not temp_is_pron_in_obj) and is_pron_in_obj and pron_obj_count == 0:
                try:
                    questions += self.who_question_obj(doc_unresolved)
                except:
                    pass
            if be_what_ques:
                w_ents = [ent for ent in sent.ents]
                if not w_ents:
                    try:
                        questions += self.what_question_subj(doc_unresolved)
                    except: 
                        pass
                    try:
                        questions += self.what_question_obj(doc_unresolved)
                    except:
                        pass
                

        # self.binary_question(self.nlp('Planks and the superstructure were tightly tied and bound together.'))
        loc_prep = ['on', 'in', 'at', 'over', 'to']
        for sent in self.resolved_sents:
            ents = [ent for ent in sent[sent.root.i:].ents if ent.label_ in ['GPE', 'LOC']]
            is_loc_prep = False
            if ents:
                for prep in loc_prep:
                    if prep in str(sent[sent.root.i:].text):
                        is_loc_prep = True
            if is_loc_prep:
                try:
                    questions += self.where_question(self.nlp(str(sent)))
                except:
                    pass
            doc = self.nlp(str(sent))
            try:
                questions += self.binary_question(doc)
            except:
                pass
        return questions

    def binary_question(self, doc):
        rating = [3, 1, 3]
        for sent in doc.sents:
            # print('*******************SENTS****************')
            if len(sent) <= 20:
                rating = [5, 3, 5]
            punc_present = False
            for token in sent[:-1]:
                if token.dep_ == 'punct':
                    punc_present = True
            if 'not' in str(sent.text) or 'this' in str(sent.text) or ',' in str(sent.text):
                rating = [i-2 for i in rating]
            if punc_present:
                rating = [i-2 for i in rating]
            root = sent.root  
            ques1, ques2, ques3 = '', '', ''
            list_of_ques_words = ['is', 'am', 'are', 'was', 'were', 'has', 'have', 'had']
            is_aux = False
            for i in range(root.i):
                if sent[i].text in list_of_ques_words:
                    aux_root = sent[i]
                    is_aux = True
                    break

            if (root.text in list_of_ques_words) or is_aux:
                if is_aux:
                    root = aux_root
                ques1 += root.text.capitalize()
                if root.text == "am":
                    ques3 += "Aren't"
                else:
                    ques3 += root.text.capitalize() + "n't"
                first_noun = self.get_first_noun_chunk(sent, root.i)
                ques1 += " " + sent[first_noun.i].text.lower() + ' ' + sent[first_noun.i+1:root.i].text
                ques3 += " " + sent[first_noun.i].text.lower() + ' ' + sent[first_noun.i+1:root.i].text
                ques2 = ques1 + " not"
                if len(sent) > 20:
                    last_noun = self.get_chunk_after_verb(sent, root.i)
                else:
                    last_noun = sent[-1]
                ques1 += " " + sent[root.i+1:last_noun.i].text + "?"
                ques2 += " " + sent[root.i+1:last_noun.i].text + "?"
                ques3 += " " + sent[root.i+1:last_noun.i].text + "?"
                if len(ques1) > 3 and ques1[-2] == '.':
                    ques1 = ques1.replace('.','')
                if len(ques2) > 3 and ques2[-2] == '.':
                    ques2 = ques2.replace('.','')
                if len(ques2) > 3 and ques3[-2] == '.':
                    ques3 = ques3.replace('.','')
                if len(ques1) < 15 or len(ques2) < 15 or len(ques2) < 15:
                    return []
        return [(ques1,rating[0]), (ques2,rating[1]), (ques3,rating[2])]
           
    
    def get_first_noun_chunk(self, doc, r_index):
        for chunk in doc[:r_index].noun_chunks:
            return doc[chunk.start]
        return doc[0]


    def get_chunk_after_verb(self, doc, r_index):
        is_chunk = False
        for chunk in doc[r_index:].noun_chunks:
            is_chunk = True
            end_token = chunk.end
            if doc[chunk.end].text == 'that':
                return doc[-1]
            if doc[chunk.end].dep_ != 'prep':
                if doc[chunk.end] == doc[-1]:
                    end_token = chunk.end
                break
        if is_chunk:
            last_token = [token for token in doc[end_token].subtree][-1]
        else:
            last_token = doc[-1]
        return last_token

    def change_3ps(self, word):
        if word[-1] == 's':
            word += 'es'
        else:
            word += 's'
        return word

    def who_question_subj(self, doc):
        ques = ''
        rating = 5
        for sent in doc.sents:
            root = sent.root
            if 'this' in str(sent.text) or ',' in str(sent.text):
                rating -= 2
            if len(sent) > 20:
                rating -= 2
                last_noun = self.get_chunk_after_verb(sent, root.i)
            else:
                last_noun = sent[-1]
            if root.text == 'am':
                ques += 'Who is ' + sent[root.i+1:last_noun.i].text + '?'
            elif root.tag_ == 'VBD' or root.tag_ == 'VBZ':
                ques += 'Who ' + doc[root.i:last_noun.i].text + '?'
            elif root.tag_ == 'VBP':
                if root.text == 'are':
                    ques += 'Who ' + self.root.text + ' ' + doc[root.i+1:last_noun.i].text + '?'
                else:
                    ques += 'Who ' + self.change_3ps(root.text) + ' ' + doc[root.i+1:last_noun.i].text + '?'
            elif root.tag_ == 'VBG' or root.tag_ == 'VBN':
                rating -= 1
                children = [child for child in root.children]
                aux_verb = None
                for w in children:
                    if w.dep_ == 'aux':
                        aux_verb = w
                        break
                if aux_verb != None and aux_verb.text == 'am':
                    ques += 'Who is ' + doc[root.i:last_noun.i].text + '?'
                elif (aux_verb != None) and ('I' in [child.text for child in children]):
                    if 'have' in [child.text for child in children]:
                        ques += 'Who has ' + doc[aux_verb.i+1:last_noun.i].text + '?'
                elif aux_verb != None:
                    ques += 'Who ' + doc[aux_verb.i:last_noun.i].text + '?'
            elif root.tag_ == 'VB':
                ques += 'Who ' + doc[root.i].text + 's ' + doc[root.i+1:last_noun.i].text + '?'
            if len(ques) > 3 and ques[-2] == '.':
                ques = ques.replace('.','')
            if len(ques) < 15:
                return []
        return [(ques, rating)]

    def who_question_obj(self, doc):
        ques = ''
        rating = 5
        for sent in doc.sents:
            root = sent.root
            if 'this' in str(sent.text) or ',' in str(sent.text):
                rating -= 2
            if len(sent) > 20:
                rating -= 2
                last_noun = self.get_chunk_after_verb(sent, root.i)
                first_noun = self.get_first_noun_chunk(sent, root.i)
            else:
                first_noun = sent[0]
                last_noun = sent[-1]
            if root.text in ['is', 'am', 'are', 'was', 'were']:
                ques += 'Who ' + root.text + ' ' + doc[first_noun.i:root.i].text.lower() + '?'
            elif root.text == 'has':
                ques += 'Who does ' + doc[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'have':
                ques += 'Who do ' + doc[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'had':
                ques += 'Who did ' + doc[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.tag_ == 'VBZ':
                ques += 'Who does ' + doc[first_noun.i:root.i].text.lower() + ' ' + root.lemma_ + '?'
            elif root.tag_ == 'VBP':
                ques += 'Who do ' + doc[first_noun.i:root.i+1].text.lower() + '?'
            elif root.tag_ == 'VBN' or root.tag_ == 'VBG':
                rating -= 1
                aux_verb = None
                children = [child for child in root.children]
                for w in children:
                    if w.dep_ == 'aux':
                        aux_verb = w
                        break
                if aux_verb != None and doc[aux_verb.i+1].dep_ == 'aux':
                    ques += 'Who ' + doc[aux_verb.i:aux_verb.i+2].text + ' ' + sent[first_noun.i:aux_verb.i].text.lower() + ' ' + + doc[root.i:last_noun.i].text + '?'
                elif aux_verb != None:
                    ques += 'Who ' + aux_verb.text + ' ' + sent[first_noun.i:aux_verb.i].text.lower() + ' ' + + doc[root.i:last_noun.i].text + '?'
            elif root.tag_ == 'VBD':
                ques += 'Who did ' + doc[first_noun.i:root.i].text.lower() + ' ' + root.lemma_
                if last_noun.i > root.i+1:
                    ques += ' ' + doc[root.i+1:last_noun.i].text
                ques += '?'
            if len(ques) > 3 and ques[-2] == '.':
                ques = ques.replace('.','')
            if len(ques) < 15:
                return []
        return [(ques, rating)]


    def where_question(self, doc):
        ques = ''
        rating = 5
        for sent in doc.sents:
            root = sent.root
            if 'this' in str(sent.text) or ',' in str(sent.text):
                rating -= 2
            if len(sent) > 20:
                rating -= 2
                last_noun = self.get_chunk_after_verb(sent, root.i)
                first_noun = self.get_first_noun_chunk(sent, root.i)
            else:
                first_noun = sent[0]
                last_noun = sent[-1]
            if root.text in ['is', 'am', 'are', 'was', 'were']:
                ques += 'Where ' + root.text + ' ' + sent[first_noun.i:root.i].text.lower() + '?'
            elif root.text == 'has':
                ques += 'Where does ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'have':
                ques += 'Where do ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'had':
                ques += 'Where did ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.tag_ == 'VBZ':
                ques += 'Where does ' + sent[first_noun.i:root.i].text.lower() + ' ' + root.lemma_ + '?'
            elif root.tag_ == 'VBP':
                ques += 'Where do ' + sent[first_noun.i:root.i+1].text.lower() + '?'
            elif root.tag_ == 'VBN' or root.tag_ == 'VBG':
                rating -= 1
                children = [child for child in root.children]
                aux_verb = None
                for w in children:
                    if w.dep_ == 'aux' or w.dep_ == 'auxpass':
                        aux_verb = w
                        break
                if aux_verb != None and sent[aux_verb.i+1].dep_ == 'aux':
                    ques += 'Where ' + sent[aux_verb.i:aux_verb.i+2].text + ' ' + sent[first_noun.i:aux_verb.i].text.lower() + ' ' + sent[root.i:last_noun.i].text + '?'
                elif aux_verb != None:
                    ques += 'Where ' + aux_verb.text + ' ' + sent[first_noun.i:aux_verb.i].text.lower() + ' ' + sent[root.i:last_noun.i].text + '?'
            elif root.tag_ == 'VBD':
                ques += 'Where did ' + sent[first_noun.i:root.i].text.lower() + ' ' + root.lemma_ 
                if last_noun.i > root.i+1:
                    ques += ' ' + sent[root.i+1:last_noun.i].text
                ques += '?'
            elif root.tag_ == 'VB':
                ques += 'Where does ' + sent[first_noun.i:root.i].text.lower() + ' do?'
            if len(ques) > 3 and ques[-2] == '.':
                ques = ques.replace('.','')
            if len(ques) < 15:
                return []
        return [(ques, rating)]

    def what_question_subj(self, doc):
        ques = ''
        rating = 3
        for sent in doc.sents:
            root = sent.root
            if 'this' in str(sent.text) or ',' in str(sent.text):
                rating -= 2
            if len(sent) > 20:
                rating -= 2
                last_noun = self.get_chunk_after_verb(sent, root.i)
                first_noun = self.get_first_noun_chunk(sent, root.i)
            else:
                first_noun = sent[0]
                last_noun = sent[-1]
            if root.tag_ == 'VBP':
                ques += 'What ' + self.change_3ps(root.text) + ' ' + sent[root.i+1:last_noun.i].text + '?'
            elif root.tag_ == 'VBG' or root.tag_ == 'VBN':
                rating -= 1
                aux_verb = None
                children = [child for child in root.children]
                for w in children:
                    if w.dep_ == 'aux' or w.dep_ == 'auxpass':
                        aux_verb = w
                        break
                if aux_verb != None:
                    ques += 'What ' + sent[aux_verb.i:last_noun.i].text + '?'
            elif root.tag_ == 'VB':
                rating -= 2
                ques += 'What ' + self.change_3ps(root.text) + '?'
            else:
                ques += 'What ' + sent[root.i:last_noun.i].text + '?'
            if len(ques) > 3 and ques[-2] == '.':
                ques = ques.replace('.','')
            if len(ques) < 15:
                return []
        return [(ques, rating)]

    def what_question_obj(self, doc):
        ques = ''
        rating = 3
        for sent in doc.sents:
            root = sent.root
            if 'this' in str(sent.text) or ',' in str(sent.text):
                rating -= 2
            if len(sent) > 20:
                rating -= 2
                last_noun = self.get_chunk_after_verb(sent, root.i)
                first_noun = self.get_first_noun_chunk(sent, root.i)
            else:
                first_noun = sent[0]
                last_noun = sent[-1]
            if root.text in ['is', 'am', 'are', 'was', 'were']:
                ques += 'What ' + root.text + ' ' + sent[first_noun.i:root.i].text.lower() + '?'
            elif root.text == 'has':
                ques += 'What does ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'have':
                ques += 'What do ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.text == 'had':
                ques += 'What did ' + sent[first_noun.i:root.i].text.lower() + ' ' + 'have?'
            elif root.tag_ == 'VBZ':
                ques += 'What does ' + sent[first_noun.i:root.i].text.lower() + ' ' + root.lemma_ + '?'
            elif root.tag_ == 'VBP':
                ques += 'What do ' + sent[first_noun.i:root.i+1].text.lower() + '?'
            elif root.tag_ == 'VBN' or root.tag_ == 'VBG':
                rating -= 1
                children = [child for child in root.children]
                aux_verb = None
                for w in children:
                    if w.dep_ == 'aux' or w.dep_ == 'auxpass':
                        aux_verb = w
                        break
                if aux_verb != None and sent[aux_verb.i+1].dep_ == 'aux':
                    ques += 'What ' + sent[aux_verb.i:aux_verb.i+2].text + ' ' + sent[first_noun.i:aux_verb.i+1].text.lower() + ' ' + sent[root.i:last_noun.i].text + '?'
                elif aux_verb != None:
                    ques += 'What ' + aux_verb.text + ' ' + sent[first_noun.i:root.i].text.lower() + ' ' + sent[root.i:last_noun.i].text + '?'
            elif root.tag_ == 'VBD':
                ques += 'What did ' + sent[first_noun.i:root.i].text.lower() + ' ' + root.lemma_ 
                if last_noun.i > root.i+1:
                    ques += ' ' + sent[root.i+1:last_noun.i].text
                ques += '?'
            elif root.tag_ == 'VB':
                ques += 'What does ' + sent[first_noun.i:root.i].text.lower() + ' do?'
            if len(ques) > 3 and ques[-2] == '.':
                ques = ques.replace('.','')
            if len(ques) < 15:
                return []
        return [(ques, rating)]
