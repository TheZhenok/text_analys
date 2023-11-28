import torch

from app.ei.base import SimpleRNN

from fastapi import FastAPI
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_ei(request: Request) -> AsyncGenerator[AsyncSession, None]:
    model = request.app.state.ei
    yield model

def generate_text(model: SimpleRNN, start_text, length=100):
    model.eval()
    with torch.no_grad():
        input_sequence = model.text_to_tensor(start_text)
        hidden_state = None
        output_text = start_text

        for _ in range(length):
            output, hidden_state = model(input_sequence, hidden_state)
            last_output = output[-1, :].argmax().item()
            output_text += model.idx_to_char[last_output]
            input_sequence = torch.tensor([last_output], dtype=torch.long)

        return output_text
    