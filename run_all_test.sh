#!/bin/bash

ROOT_DIR=$(pwd)
OUT_DIR="$ROOT_DIR/results-new"
ITERATIONS=5

declare -A TESTS=(
  [rest_no_ssl]="test/test-not-ssl/load_test_rest.js"
  [rest_ssl]="test/test-ssl/ssl_load_test_rest.js"
  [graphql_no_ssl]="test/test-not-ssl/load_test_graphql.js"
  [graphql_ssl]="test/test-ssl/ssl_load_test_graphql.js"
  [grpc_ssl]="test/test-ssl/ssl_load_test_grpc.js"
  [grpc_no_ssl]="test/test-not-ssl/load_test_grpc.js"
)

for name in "${!TESTS[@]}"; do
  script="${ROOT_DIR}/${TESTS[$name]}"
  export_path="$OUT_DIR/$name"

  echo "▶️ Starting test: $name"
  mkdir -p "$export_path"

  for i in $(seq 1 $ITERATIONS); do
    echo "   ⏱ Run $i/$ITERATIONS..."
    k6 run --summary-export="$export_path/run_${i}.json" "$script" > /dev/null
    if [ $? -ne 0 ]; then
      echo "❌ Error on run $i of $name — check script path or k6 output"
      exit 1
    fi
  done

  echo "✅ Finished test: $name"
  echo ""
done

echo "🎉 All tests complete. Results in '$OUT_DIR/'"
