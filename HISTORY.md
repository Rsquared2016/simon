##vNEXT

* GPU acceleration
* Heterogeneous acceleration (multiple CPUs, GPUs)

##v1.2.0
* Added transfer learning capability via Classifier.generate_transfer_model method
* Includes a new method, that guesses categorical/ordinal type classification based on some fixed statistical/proportion rules
* Includes pretrained models of base types + categorical/ordinal and base types + categorical/ordinal + 6 geographical categories 

##v1.1.0
* First pip-installable version
* CNN+LSTM learning for text classification
* Includes pretrained model Base.pkl for semantic classification of 9 base types - 'address', 'boolean', 'datetime', 'email', 'float', 'int', 'phone', 'text', 'uri'