#!/bin/bash

TEST_NAME=$1         # например: rest
SCRIPT=$2            # путь к .js файлу
COUNT=$3             # сколько прогонов
OUT_DIR="results/$TEST_NAME"

mkdir -p $OUT_DIR

for i in $(seq 1 $COUNT); do
  k6 run --summary-export="$OUT_DIR/run_${i}.json" $SCRIPT
done
