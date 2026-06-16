from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

text = "My credit card was charged twice."

embedding = model.encode(text)

print(type(embedding))
print(embedding.shape)
