# Bi-encoder models

First-stage encoders independently map chunks and queries into the same vector
space. The built-in flow includes lexical hashing and corpus-fitted LSA without
weights here. Attention-based Sentence Transformers should be placed under
`artifacts/<model-name>/` and referenced by local path from a configuration.
