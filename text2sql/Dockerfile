FROM nvcr.io/nvidia/pytorch:23.06-py3

RUN pip3 install --upgrade pip && pip3 install accelerate fschat transformers snowflake-snowpark-python pandas jupyterlab peft accelerate bitsandbytes sqlglot jsonlines datasets
RUN apt-get update && \
    apt-get install -y git curl rsync && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install git-lfs && \
    git lfs install


# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

ENV HUGGING_FACE_MODEL=NumbersStation/nsql-llama-2-7B

RUN apt-get update && apt-get install -y --no-install-recommends

WORKDIR /notebooks
# Copy Notebooks and data into the container at /notebooks

# COPY FineTuneModel.ipynb .
# COPY AudioCalls_FineTuning_Dataset.csv .
# COPY download_model.sh .
# COPY Webservice.py .

COPY ./ /notebooks

# RUN conda install -n audiollm -c https://repo.anaconda.com/pkgs/snowflake snowflake-snowpark-python pandas jupyterlab

# Make port 8888 available to the world outside this container
# EXPOSE 8888

# Run JupyterLab on port 8888 when the container launches
CMD ["jupyter","lab" ,"--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root","--NotebookApp.token=''", "--NotebookApp.password=''"]
# ENTRYPOINT ["/RunFastAPI.sh"]
# CMD ["/opt/conda/envs/rapids/bin/jupyter", "llm-finetune", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
