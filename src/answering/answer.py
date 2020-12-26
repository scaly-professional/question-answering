import torch
from models import InferSent
import sys
from scipy import spatial
import numpy
import math
from nltk.tokenize import sent_tokenize

def QuestionGenCos(A,Q):
   cosineSimilarity = float("-inf")
   AIndex = 0
   #magnitudeQ = numpy.linalg.norm(numpy.array(Q))
   for (i,sentences) in enumerate(A):
      cosSim = 1 - spatial.distance.cosine(sentences, Q)
      if cosSim > cosineSimilarity:
         cosineSimilarity = cosSim
         AIndex = i
   return AIndex

fileName = sys.argv[1]
questionFile = sys.argv[2]


sentences = []
with open(fileName, 'r') as fileinput:
   for line in fileinput:
       sentences.append(line)

questions = []
with open(questionFile, 'r') as fileinput:
   for line in fileinput:
      questions.append(line)

V = 1
MODEL_PATH = 'encoder/infersent%s.pkl' % V
params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
infersent = InferSent(params_model)
infersent.load_state_dict(torch.load(MODEL_PATH))
W2V_PATH = 'fastText/crawl-300d-2M.vec'
infersent.set_w2v_path(W2V_PATH)
infersent.build_vocab(sentences, tokenize=True)

sent_embeddings = infersent.encode(sentences, tokenize=True)
ques_embeddings = infersent.encode(questions, tokenize=True)

answers = []
for i in range(len(questions)):
    questionvec = ques_embeddings[i]
    index = QuestionGenCos(sent_embeddings, questionvec)
    answers.append(questions[i] + ": " + sentences[index])
for answer in answers:
    print(answer + "\n")