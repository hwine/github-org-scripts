FROM jupyter/minimal-notebook:hub-2.1.1

# add in the extensions we need
RUN    conda install -y -c conda-forge jupyter_contrib_nbextensions ; \
       jupyter nbextensions_configurator enable ; \
       jupyter nbextension enable init_cell/main ; \
       jupyter nbextension enable collapsible_headings/main ; \
       jupyter nbextension list

# install the packages needed
COPY    requirements.txt .
RUN     pip install -r requirements.txt

# install the notebooks and trust the notebooks we ship
COPY notebooks/*.ipynb ./work/
RUN    echo "pwd $PWD" ; \
       echo "ls: $(ls -lAd work/*.ipynb)" ; \
       jupyter trust work/*.ipynb
