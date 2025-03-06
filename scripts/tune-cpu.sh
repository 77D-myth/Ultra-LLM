#!/bin/bash
# Optimize CPU affinity/threading for llama.cpp
CORES=$(lscpu | grep 'CPU(s):' | awk '{print $2}')
PHY_CORES=$(lscpu | grep 'Core(s) per socket' | awk '{print $4}')
LOGICAL_CORES=$((CORES / PHY_CORES))

echo "🔄 Setting CPU affinity for $PHY_CORES physical cores ($LOGICAL_CORES threads/core)"

# Pin to physical cores only
TASKSET_CMD="taskset -c 0-$((PHY_CORES - 1))"

# Configure OpenBLAS for single-threaded mode
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=$PHY_CORES

echo "🚀 Starting with optimized settings:"
$TASKSET_CMD python app.py --threads $PHY_CORES
