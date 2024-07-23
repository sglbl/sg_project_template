import torch
from gliner import GLiNER # type: ignore
from huggingface_hub import hf_hub_download, snapshot_download
import joblib

# first load your model
def save_model(current_model, path):
    config = current_model.config
    dict_save = {"model_weights": current_model.state_dict(), "config": config}
    torch.save(dict_save, path)


def load_model(path, model_name=None):
    
    dict_load = torch.load(path, map_location=torch.device('cpu'))
    config = dict_load["config"]

    print(f"'{config.model_name}' should be available for local processing")

    if model_name is not None:
        config.model_name = model_name

    loaded_model = GLiNER(config)
    loaded_model.load_state_dict(dict_load["model_weights"])
    return loaded_model

if __name__ == "__main__":
    print(f"Starting to save GLiNER model")
    model = GLiNER.from_pretrained("urchade/gliner_multi")
    save_model(model, "./models/gliner_model_weight.pt")
    
    print('Downloading MDeBERTa model')
    try:
        model = joblib.load(
            snapshot_download(repo_id="microsoft/mdeberta-v3-base", local_dir="./models/mdeberta-v3-base/")
        )
    except Exception as e:
        pass