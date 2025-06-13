
# from config.header import *

import torch
import torch.nn.functional as F
import torch.nn as nn
from transformers import BertTokenizer
from transformers import BertModel, BertConfig


class SimcseSupModel(nn.Module):

    def __init__(self, pretrained_bert_path, drop_out) -> None:

        super(SimcseSupModel, self).__init__()

        self.pretrained_bert_path = pretrained_bert_path
        config = BertConfig.from_pretrained(self.pretrained_bert_path)
        config.attention_probs_dropout_prob = drop_out
        config.hidden_dropout_prob = drop_out
        self.bert = BertModel.from_pretrained(self.pretrained_bert_path, config=config)

    def forward(self, input_ids, attention_mask, token_type_ids, pooling="cls"):
        out = self.bert(input_ids, attention_mask, token_type_ids, output_hidden_states=True)

        if pooling == "cls":
            return out.last_hidden_state[:, 0]
        if pooling == "pooler":
            return out.pooler_output
        if pooling == 'last-avg':
            last = out.last_hidden_state.transpose(1, 2)
            return torch.avg_pool1d(last, kernel_size=last.shape[-1]).squeeze(-1)
        if self.pooling == 'first-last-avg':
            first = out.hidden_states[1].transpose(1, 2)
            last = out.hidden_states[-1].transpose(1, 2)
            first_avg = torch.avg_pool1d(first, kernel_size=last.shape[-1]).squeeze(-1)
            last_avg = torch.avg_pool1d(last, kernel_size=last.shape[-1]).squeeze(-1)
            avg = torch.cat((first_avg.unsqueeze(1), last_avg.unsqueeze(1)), dim=1)
            return torch.avg_pool1d(avg.transpose(1, 2), kernel_size=2).squeeze(-1)


class SimcseUnsupModel(nn.Module):

    def __init__(self, pretrained_bert_path, drop_out) -> None:

        super(SimcseUnsupModel, self).__init__()

        self.pretrained_bert_path = pretrained_bert_path
        config = BertConfig.from_pretrained(self.pretrained_bert_path)
        config.attention_probs_dropout_prob = drop_out
        config.hidden_dropout_prob = drop_out
        self.bert = BertModel.from_pretrained(self.pretrained_bert_path, config=config)

    def forward(self, input_ids, attention_mask, token_type_ids, pooling="cls"):
        out = self.bert(input_ids, attention_mask, token_type_ids, output_hidden_states=True)

        if pooling == "cls":
            return out.last_hidden_state[:, 0]
        if pooling == "pooler":
            return out.pooler_output
        if pooling == 'last-avg':
            last = out.last_hidden_state.transpose(1, 2)
            return torch.avg_pool1d(last, kernel_size=last.shape[-1]).squeeze(-1)
        if self.pooling == 'first-last-avg':
            first = out.hidden_states[1].transpose(1, 2)
            last = out.hidden_states[-1].transpose(1, 2)
            first_avg = torch.avg_pool1d(first, kernel_size=last.shape[-1]).squeeze(-1)
            last_avg = torch.avg_pool1d(last, kernel_size=last.shape[-1]).squeeze(-1)
            avg = torch.cat((first_avg.unsqueeze(1), last_avg.unsqueeze(1)), dim=1)
            return torch.avg_pool1d(avg.transpose(1, 2), kernel_size=2).squeeze(-1)


class Simcse:

    def __init__(self, conf):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.bert_path = conf.bert_path
        self.model_path = conf.model_path

        self.model = self.build_model(conf.model_type)
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)

        self.cache = {}

        self.dim = 768

    def build_model(self, model_type):

        # model_path = f'{project_path}/checkpoint/simcse_{model_type}.pt'

        if model_type == "unsup":
            model = SimcseUnsupModel(
                pretrained_bert_path=self.bert_path,
                drop_out=0.3
            ).to(self.device)
        else:
            model = SimcseSupModel(
                pretrained_bert_path=self.bert_path,
                drop_out=0.3
            ).to(self.device)

        model.load_state_dict(
            torch.load(
                self.model_path,
                map_location=self.device
            )
        )
        model.eval()
        return model

    def pred(self, text_):

        if text_ in self.cache.keys():
            return self.cache[text_]

        token_a = self.tokenizer([text_], max_length=64, truncation=True, padding='max_length', return_tensors='pt')

        with torch.no_grad():
            source_input_ids = token_a.get('input_ids').squeeze(1).to(self.device)
            source_attention_mask = token_a.get('attention_mask').squeeze(1).to(self.device)
            source_token_type_ids = token_a.get('token_type_ids').squeeze(1).to(self.device)
            source_pred = self.model(source_input_ids, source_attention_mask, source_token_type_ids)

            self.cache[text_] = source_pred
            return source_pred.cpu()

    def run(self, text_a, text_b):

        a = self.pred(text_a)
        b = self.pred(text_b)

        sim = F.cosine_similarity(a, b, dim=-1).item()
        return sim

