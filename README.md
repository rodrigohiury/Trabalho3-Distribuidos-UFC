# Trabalho 2 - Sistemas Distribuidos - UFC
# Casa Inteligente

Universidade Federal do Ceará  
Disciplina de Sistemas Distribuídos  
Semestre 2025.2  

## Integrantes:
Eduardo Monteiro de Sousa - 538045  
Leonardo Monteiro de Sousa - 540707  
Luis Carlos Rodrigues dos Anjos - 509022  
Rodrigo Hiury Silva Araújo - 397843

## Overview do Projeto
[Vídeo no Google Drive](https://drive.google.com/file/d/1b_QKlAXomHBmaBuYhUpqyVx81ocL84-1/view?usp=sharing)

## Visão Geral do Sistema
Neste trabalho, foi desenvolvido um sistema simples baseado em sensores e atuadores distribuídos, onde diferentes dispositivos (como sensores de temperatura, luz e som, além de atuadores como ar-condicionado e controladores) se comunicam com um gateway central utilizando protocolo protobuf. O gateway atua como intermediário, concentrando a comunicação, gerenciando estados e expondo uma interface para um cliente web, que permite monitorar os dados dos sensores em tempo real e enviar comandos aos atuadores. O objetivo é permitir o monitoramento e o controle remoto de dispositivos físicos simulados, garantindo comunicação padronizada, baixo acoplamento e facilidade de expansão.

## Arquitetura
O sistema é dividido em três camadas principais:

**1. Dispositivos (Sensores e Atuadores)**

Cada sensor ou atuador é implementado como um processo independente. Sensores são responsáveis por coletar ou simular dados do ambiente (como temperatura, luz e som), enquanto atuadores executam ações (por exemplo, ligar/desligar um ar-condicionado). Esses dispositivos não se comunicam diretamente com o cliente, apenas com o gateway, o que evita dependências diretas e aumenta a segurança e a escalabilidade do sistema. Os dispositivos atuantes nesse projeto são uma Luz de quarto, Um portão automático e Um sensor de temperatura, e são simulados em python.

**2. Gateway**

O gateway é o núcleo do sistema distribuído. Ele recebe conexões dos sensores e atuadores, processa suas mensagens, mantém o estado atual de cada dispositivo e centraliza a lógica de controle. Além disso, o gateway é implementado em python e expõe uma interface de comunicação para o cliente web, funcionando como um ponto único de acesso ao sistema. Essa abordagem reduz a complexidade da comunicação e permite que novos dispositivos sejam adicionados sem alterar o cliente.

**3. Cliente Web**

O cliente web é a interface do usuário final. Ele se comunica exclusivamente com o gateway, solicitando leituras de sensores e enviando comandos para os atuadores. A interface implementada em HTML/CSS e JS e permite visualizar o estado dos dispositivos em tempo real e interagir com eles de forma simples e intuitiva, abstraindo completamente os detalhes de rede e implementação dos nós distribuídos.

## Instalação

Para simular o sistema, é necessário instalar os módulos de forma individual. 

### 1. Cliente

Para rodarmos o cliente, primeiro configuraremos o ambiente virtual do python. Primeiro, devemos mudar para a pasta referente ao cliente, usando o comando:
```
cd src/client/app
```
Com o python instalado na máquina. Roda-se o comando:
```
python -m venv .venv
```
Após criarmos o ambiente virtual do python, precisamos ativá-lo. No linux, o comando é:
```
.venv/bin/activate
```
Para sistemas operacionais Windows, o comando é:
```
.venv/Scripts/Activate.ps1
```
Após ativar o ambiente virtual, podemos voltar a pasta client dando:
```
cd ..
```
E então, instalamos os pacotes necessários para a aplicação através do comando:
```
pip install -r requirements.txt
```
Com esse processo concluído, podemos rodar a aplicação com o comando:
```
uvicorn app.main:app --reload --port 8000
```
Após a instalação, pode-se rodar novamente o cliente simplesmente rodando o script na raíz do projeto:
```
client.ps1
```

### 2. Gateway

Para rodarmos o gateway, passamos por um processo parecido. Primeiro, configuraremos o ambiente virtual do python. Para isso, devemos mudar para a pasta referente ao gateway, usando o comando:
```
cd src/gateway
```
Com o python instalado na máquina. Roda-se o comando:
```
python -m venv .venv
```
Após criarmos o ambiente virtual do python, precisamos ativá-lo. No linux, o comando é:
```
.venv/bin/activate
```
Para sistemas operacionais Windows, o comando é:
```
.venv/Scripts/Activate.ps1
```
E então, instalamos os pacotes necessários para a aplicação através do comando:
```
pip install -r requirements.txt
```
Com esse processo concluído, podemos rodar a aplicação com o comando:
```
python main.py
```
Após a instalação, pode-se rodar novamente o gateway simplesmente rodando o script na raíz do projeto:
```
gateway.ps1
```

## 3. Dispositivo Luz do Quarto

Para rodarmos o dispositivo luz do quarto, passamos por um processo parecido. Primeiro, configuraremos o ambiente virtual do python. Para isso, devemos mudar para a pasta referente ao gateway, usando o comando:
```
cd src/luz-quarto
```
Com o python instalado na máquina. Roda-se o comando:
```
python -m venv .venv
```
Após criarmos o ambiente virtual do python, precisamos ativá-lo. No linux, o comando é:
```
.venv/bin/activate
```
Para sistemas operacionais Windows, o comando é:
```
.venv/Scripts/Activate.ps1
```
E então, instalamos os pacotes necessários para a aplicação através do comando:
```
pip install -r requirements.txt
```
Com esse processo concluído, podemos rodar a aplicação com o comando:
```
python main.py
```
Após a instalação, pode-se rodar novamente o dispositivo luz do quarto simplesmente rodando o script na raíz do projeto:
```
luz-quarto.ps1
```

## 4. Dispositivo Portão Automático

Para rodarmos o dispositivo portão automático, passamos por um processo parecido. Primeiro, configuraremos o ambiente virtual do python. Para isso, devemos mudar para a pasta referente ao gateway, usando o comando:
```
cd src/porta-auto
```
Com o python instalado na máquina. Roda-se o comando:
```
python -m venv .venv
```
Após criarmos o ambiente virtual do python, precisamos ativá-lo. No linux, o comando é:
```
.venv/bin/activate
```
Para sistemas operacionais Windows, o comando é:
```
.venv/Scripts/Activate.ps1
```
E então, instalamos os pacotes necessários para a aplicação através do comando:
```
pip install -r requirements.txt
```
Com esse processo concluído, podemos rodar a aplicação com o comando:
```
python main.py
```
Após a instalação, pode-se rodar novamente o gateway simplesmente rodando o script na raíz do projeto:
```
porta.ps1
```

## 5. Disposivo Sensor de Temperatura

Para rodarmos o dispositivo sensor de temperatura, passamos por um processo parecido. Primeiro, configuraremos o ambiente virtual do python. Para isso, devemos mudar para a pasta referente ao gateway, usando o comando:
```
cd src/temp-sensor
```
Com o python instalado na máquina. Roda-se o comando:
```
python -m venv .venv
```
Após criarmos o ambiente virtual do python, precisamos ativá-lo. No linux, o comando é:
```
.venv/bin/activate
```
Para sistemas operacionais Windows, o comando é:
```
.venv/Scripts/Activate.ps1
```
E então, instalamos os pacotes necessários para a aplicação através do comando:
```
pip install -r requirements.txt
```
Com esse processo concluído, podemos rodar a aplicação com o comando:
```
python main.py
```
Após a instalação, pode-se rodar novamente o gateway simplesmente rodando o script na raíz do projeto:
```
temp-sensor.ps1
```

