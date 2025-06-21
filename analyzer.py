import torch
from transformers import pipeline


class MessageAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            'zero-shot-classification',
            model='facebook/bart-large-mnli',
            device=0 if torch.cuda.is_available() else -1
        )
        self.target_labels = ('amusing', 'insult', 'interesting', 'creative', 'silly', 'thoughtful', 'much text', 'low-effort')

    def analyse_message(self, content: str) -> float:
        if len(content) < 10:
            return 0
        result = self.classifier(content, candidate_labels=self.target_labels, multi_label=False)
        scores = dict(zip(result['labels'], result['scores']))

        scores = (
            scores.get('amusing', 0),
            scores.get('insult', 0),
            scores.get('interesting', 0),
            scores.get('effort', 0),
            scores.get('creative', 0),
            scores.get('silly', 0),
            scores.get('thoughtful', 0),
            scores.get('much text', 0),
            scores.get('low-effort', 0),
        )

        scores_final = (
            0.4 * scores[0],
            0.5 * scores[1],
            0.4 * scores[2],
            0.3 * scores[3],
            0.3 * scores[4],
            0.3 * scores[5],
            0.3 * scores[6],
            1.5 * scores[7],
            -1 * scores[8]
        )
        print(scores)
        return sum(scores_final)

    def test(self):
        for msg in ["""@Utonish Members of this server are sending fraudulent texts as private messages in the hope of extorting money from me. They pretend to be you in order to legitimise themselves, although it is obvious that they are imitations. I hereby request you to block karottenhoe whose identity has been verified by the fake account. Please act now to prevent your server from becoming a place of hate and criminality."""]:
            print(self.analyse_message(msg))