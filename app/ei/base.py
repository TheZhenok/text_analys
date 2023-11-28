import torch
import torch.nn as nn
import torch.optim as optim
import fitz

from fastapi import FastAPI


class SimpleRNN(nn.Module):
    # def read_book(self) -> str:
    #     doc = fitz.open("app/Emma.pdf")
    #     text = ""

    #     for page_number in range(doc.page_count):
    #         page = doc[page_number]
    #         text += page.get_text()

    #     doc.close()
    #     return text

    def __init__(self):
        super(SimpleRNN, self).__init__()

    def forward(self, x, hidden):
        x = self.embedding(x)
        out, hidden = self.rnn(x, hidden)
        out = self.fc(out)
        return out, hidden
    
    def text_to_tensor(self, text):
        return torch.tensor([self.char_to_idx[char] for char in text], dtype=torch.long)
    
    def start_up(self) -> None:
        # corpus = self.read_book()
        corpus = """
        Mr. Woodhouse was fond of society in his own way. He liked very much to
        have his friends come and see him; and from various united causes, from his
        long residence at Hartfield, and his good nature, from his fortune, his house, and
        his daughter, he could command the visits of his own little circle, in a great
        measure, as he liked. He had not much intercourse with any families beyond that
        circle; his horror of late hours, and large dinner-parties, made him unfit for any
        acquaintance but such as would visit him on his own terms. Fortunately for him,
        Highbury, including Randalls in the same parish, and Donwell Abbey in the
        parish adjoining, the seat of Mr. Knightley, comprehended many such. Not
        unfrequently, through Emma's persuasion, he had some of the chosen and the
        best to dine with him: but evening parties were what he preferred; and, unless he
        fancied himself at any time unequal to company, there was scarcely an evening
        in the week in which Emma could not make up a card-table for him.
        Real, long-standing regard brought the Westons and Mr. Knightley; and by
        Mr. Elton, a young man living alone without liking it, the privilege of
        exchanging any vacant evening of his own blank solitude for the elegancies and
        society of Mr. Woodhouse's drawing-room, and the smiles of his lovely daughter,
        was in no danger of being thrown away.
        After these came a second set; among the most come-at-able of whom were
        Mrs. and Miss Bates, and Mrs. Goddard, three ladies almost always at the
        service of an invitation from Hartfield, and who were fetched and carried home
        so often, that Mr. Woodhouse thought it no hardship for either James or the
        horses. Had it taken place only once a year, it would have been a grievance.
        """

        self.chars = sorted(list(set(corpus)))
        self.char_to_idx = {char: idx for idx, char in enumerate(self.chars)}
        self.idx_to_char = {idx: char for idx, char in enumerate(self.chars)}

        input_data = self.text_to_tensor(corpus[:-1])
        target_data = self.text_to_tensor(corpus[1:])

        hidden_size = 100
        input_size = len(self.chars)
        output_size = len(self.chars)
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.rnn = nn.RNN(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.parameters(), lr=0.01)
        num_epochs = 1000

        for epoch in range(num_epochs):
            optimizer.zero_grad()
            hidden_state = None
            output, hidden_state = self(input_data, hidden_state)
            loss = criterion(output.view(-1, output_size), target_data.view(-1))
            loss.backward()
            optimizer.step()

            if (epoch + 1) % 100 == 0:
                print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')
        
    
def _setup_ei(app: FastAPI):
    model = SimpleRNN()
    model.start_up()
    app.state.ei = model


# generated_text = generate_text(model, start_text_for_generation, length=200)

# Hello
# 21 2 3 3 5 = 34
# 21^ 2 2^2 3^2 = 3572100
# My
# 30 4 = 34
# 14400