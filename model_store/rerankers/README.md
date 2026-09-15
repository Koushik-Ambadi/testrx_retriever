# Cross-encoder models

Cross-encoders jointly score a query and candidate chunk after first-stage
retrieval. The built-in lexical pairwise scorer validates the complete reranking
flow. Attention-based weights belong under `artifacts/<model-name>/` and are
loaded only when explicitly selected in configuration.
