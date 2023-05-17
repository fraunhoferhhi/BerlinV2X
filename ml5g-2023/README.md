# Multi-environment automotive QoS prediction using AI/ML

The Berlin V2X dataset forms the problem statement
_"Multi-environment automotive QoS prediction using AI/ML"_ at
[ITU AI/ML in 5G Challenge 2023](https://aiforgood.itu.int/about-ai-for-good/aiml-in-5g-challenge/).

## Description

The challenge consists in the prediction of QoS for the cellular communication in the
[BerlinV2X dataset](https://ieee-dataport.org/open-access/berlin-v2x).
Any LTE, geographical or side information parameters can be taken as the input features, while uplink and/or downlink throughput will be set as the predicted QoS parameters.
Moreover, a multi-domain approach is required.
That is, the cellular QoS prediction algorithm will be trained in a particular source domain and tested in a different target domain,
possibly fine-tuned via transfer learning or domain adaptation techniques.
One possible option is to consider operators as different domains.
In this case, one operator will serve as the source domain and the other one as target domain.
However, you can also pose source and target domain differently, for instance:

- **Link direction**: Train a QoS predictor for uplink throughput and adapt to downlink throughput.
- **Areas**: E.g., “Highway” as source domain and “Residential” as target domain.
- **Cars**: Pick different cars (served by the same operator or not) for source and target domains.

## Evaluation

We offer a preprocessed data-bundle, *cellular_dataframe.parquet*, that can be used as such, where all different data sources have been downsampled to 1 second and merged together. Nevertheless, we encourage participants to create their own preprocessed datasets (e.g. through upsampled/interpolated GPS traces) if this better suits their needs. For this, the participants can take the existing code base as a starting point. Contributions to the code repository are equally appreciated.

Feature engineering will be evaluated. As an example, if two models attain similar accuracy, but one model uses all PHY layer parameters and the other model only uses SNR, the latter model will be preferred.

### Evaluation score

The final score will be computed as the weighted mean of:

- The coefficient of determination $R^2$ of the model on the test data. The $R^2$ score is computed in most ML/DL libraries as 
$R^2(y, \hat{y}) = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}$
- The discarded features. More specifically, since we consider the dataset to contain 84 useful features, this partial score equals `84 - used_features`.
- A qualitative score depending on the problem setup, e.g., the decisions on the QoS parameter and the train/test split.

We provide a [reference notebook](./reference_notebook.ipynb)
were the predicted QoS parameters is downlink datarate
and the train and test sets consist of the data from orpeator 1 and operator 2, respectively.

### Submission

The participants will submit the following in the
[ITU's challenge platform](https://challenge.aiforgood.itu.int/match/matchitem/80):

- Their code implementation.
- A CSV file (see the reference [scores.csv](./scores.csv)) containing:
	- Their Team ID
	- Their predicted QoS (e.g., "downlink QoS")
	- Their train and test sets (e.g., "operator 1" and "operator 2")
	- Their $R^2$ score
	- The number of used features

- A short written report (2-5 pages) in .docx or PDF. The participants need to justify their design choices (e.g. the type of domain adaptation problem and the chosen domains).
- Optionally, the saved model and weights in a suitable format.

## Timeline

tbd