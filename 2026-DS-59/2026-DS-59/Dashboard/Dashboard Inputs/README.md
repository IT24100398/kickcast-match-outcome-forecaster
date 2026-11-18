# Match Outcome Dashboard (Streamlit)

## Files
- app.py - the dashboard
- train_model.py - trains the two Random Forest models and creates the chart tables (run once)
- train_final*.csv, test_final*.csv, final_feature_sets.json, results_*.csv - inputs from the notebooks
- requirements.txt

## Run on your computer
    pip install -r requirements.txt
    python train_model.py
    streamlit run app.py

## Run from Google Colab
Upload all files to /content, then run these cells:

    !pip install -q streamlit
    !python train_model.py
    !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared
    !nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
    !./cloudflared tunnel --url http://localhost:8501

Open the https://....trycloudflare.com link printed at the end.

Run train_model.py in your own environment (do not reuse .joblib files from another machine), because saved models can break between scikit-learn versions.
