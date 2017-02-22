#!/usr/bin/env bash

declare -a MODELS=(
    "oberiu-ru"
    "aragon-ru"
    "vvedensky-ru --model vvedensky-ru-3-512"
    "mcdonagh-ru"
    "brodsky-ru"
    "tinyshakespeare-ru"
    "pillowbook-ru"
    "kafka-ru"
    "aeneid-mixed-ua"
)

rm -f training-progress.txt

for m in "${MODELS[@]}"
do
   echo "${m}" >> training-progress.txt
    ./main.py --train ${m}
done

zip -r char-rnn-models.zip save/*

