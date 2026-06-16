#!/usr/bin/env bash
# cache_performance_analyzer.sh - 自动化缓存性能测试工具
# 实验配置：包含标准模式(all_sim/)和Victim Cache增强模式(all_sim_victim/)
# 测试维度：基准配置、容量扫描、相联度扫描、块大小扫描，共计三个benchmark
# 智能执行：自动检测已完成任务并跳过，支持断点续跑

set -euo pipefail

# ====== 模拟器配置参数 ======
SIMULATOR_BIN="./sim-cache"
CONFIG_FILE="-config two_level.cfg"      # 配置文件路径，留空则不使用

# ====== 测试基准程序配置 ======
BENCHMARK_MCF="./mcf00.peak.ev6 mcf.lgred.in"
BENCHMARK_VORTEX="./vortex00.peak.ev6 vortex.lgred.raw"   # vortex基准测试
BENCHMARK_BZIP2="./bzip200.peak.ev6 bzip2.lgred.graphic 1"

# ====== L1缓存参数设置：容量16KB、相联度2、块大小64B、替换策略LRU ======
L1_ICACHE="il1:128:64:2:l"
L1_DCACHE="dl1:128:64:2:l"
L2_UNIFIED_ALIAS="dl2"  # 统一L2缓存配置：il2映射到dl2

get_timestamp() { date "+%F %T"; }

# ====== 结果输出目录初始化 ======
OUTPUT_DIR_STANDARD="all_sim"
OUTPUT_DIR_VICTIM="all_sim_victim"
mkdir -p "${OUTPUT_DIR_STANDARD}/baseline" "${OUTPUT_DIR_STANDARD}/cap" "${OUTPUT_DIR_STANDARD}/way" "${OUTPUT_DIR_STANDARD}/blk"
mkdir -p "${OUTPUT_DIR_VICTIM}/baseline"   "${OUTPUT_DIR_VICTIM}/cap"   "${OUTPUT_DIR_VICTIM}/way"   "${OUTPUT_DIR_VICTIM}/blk"

# ====== 检查日志文件完整性 ======
validate_log_completion() {
  local log_file="$1"
  [[ -s "$log_file" ]] && grep -q "^sim: \*\* simulation statistics \*\*" "$log_file" && grep -q "^ul2\.misses" "$log_file"
}

# ====== 执行单个测试实例 ======
execute_single_test() {
  local test_category="$1" capacity_kb="$2" associativity="$3" block_size="$4" \
        bench_id="$5" bench_command="$6" log_output="$7" victim_cache_mode="$8"

  # 检测任务是否已完成，若已完成则跳过
  if validate_log_completion "${log_output}"; then
    echo "⏭ 跳过  $(get_timestamp)  [${test_category}]  (${bench_id})  → ${log_output}  (任务已完成)"
    return 0
  fi

  # 计算L2缓存组数：总容量 = 组数 × 块大小 × 相联度
  local total_bytes=$(( capacity_kb * 1024 ))
  local num_sets=$(( total_bytes / (block_size * associativity) ))
  if (( num_sets <= 0 )); then
    echo "[警告] 缓存配置无效: 容量=${capacity_kb}KB 相联度=${associativity} 块大小=${block_size}" >&2
    return 1
  fi
  local L2_CONFIG="ul2:${num_sets}:${block_size}:${associativity}:l"
  local vc_status="关闭"; [[ "${victim_cache_mode}" == "on" ]] && vc_status="启用"

  # —— 控制台输出：任务开始提示 —— 
  echo ""
  echo "▶ 开始  $(get_timestamp)  [${test_category}]"
  echo "   基准程序=${bench_command}"
  echo "   L1I=${L1_ICACHE} | L1D=${L1_DCACHE} | L2=ul2:${capacity_kb}KB,assoc=${associativity},blk=${block_size}B(sets=${num_sets}) 统一缓存(il2->dl2), Victim Cache=${vc_status}"
  echo "   日志文件=${log_output}"

  # —— 写入日志文件头部信息 —— 
  {
    echo "============================================================"
    echo "[`get_timestamp`] 测试类别=${test_category}  基准程序=${bench_command}"
    echo "[配置] Victim Cache=${vc_status}"
    echo "[配置] L1缓存: ${L1_ICACHE} | ${L1_DCACHE}"
    echo "[配置] L2缓存: ${L2_CONFIG} (统一缓存, LRU策略), il2 -> dl2"
    echo "------------------------------------------------------------"
  } > "${log_output}"

  # —— 开始模拟执行 —— 
  local start_time end_time elapsed_time return_code
  start_time=$(date +%s)
  set +e
  if [[ "${victim_cache_mode}" == "on" ]]; then
    ${SIMULATOR_BIN} ${CONFIG_FILE} \
      -cache:il1 "${L1_ICACHE}" \
      -cache:dl1 "${L1_DCACHE}" \
      -cache:il2 "${L2_UNIFIED_ALIAS}" \
      -cache:dl2 "${L2_CONFIG}" \
      -vc true \
      ${bench_command} >> "${log_output}" 2>&1
  else
    ${SIMULATOR_BIN} ${CONFIG_FILE} \
      -cache:il1 "${L1_ICACHE}" \
      -cache:dl1 "${L1_DCACHE}" \
      -cache:il2 "${L2_UNIFIED_ALIAS}" \
      -cache:dl2 "${L2_CONFIG}" \
      ${bench_command} >> "${log_output}" 2>&1
  fi
  return_code=$?
  set -e
  end_time=$(date +%s); elapsed_time=$(( end_time - start_time ))

  # —— 提取关键性能指标并追加到日志 —— 
  {
    echo "------------------------------------------------------------"
    echo "[性能统计摘要: L1/L2缓存关键指标]"
    grep -E '^il1\.(accesses|hits|misses|miss_rate|replacements|writebacks)\b'  "${log_output}" | sed 's/^/  /' || true
    grep -E '^dl1\.(accesses|hits|misses|miss_rate|replacements|writebacks)\b'  "${log_output}" | sed 's/^/  /' || true
    grep -E '^dl1\.vc_hits\b'    "${log_output}" | sed 's/^/  /' || true
    grep -E '^dl1\.vc_misses\b'  "${log_output}" | sed 's/^/  /' || true
    grep -E '^ul2\.(accesses|hits|misses|miss_rate|replacements|writebacks)\b'  "${log_output}" | sed 's/^/  /' || true
    echo "============================================================"
  } >> "${log_output}"

  # —— 控制台输出：任务完成或失败状态 —— 
  if validate_log_completion "${log_output}"; then
    echo "✓ 完成   $(get_timestamp)  [${test_category}]  (耗时${elapsed_time}秒)  → ${log_output}"
    return 0
  else
    echo "✗ 失败   $(get_timestamp)  [${test_category}]  (返回码=${return_code}, 耗时${elapsed_time}秒)  → ${log_output}"
    return 1
  fi
}

# ====== 基准程序集合定义 ======
declare -A BENCHMARK_SET=(
  [data1]="$BENCHMARK_MCF"      # mcf基准
  [data2]="$BENCHMARK_VORTEX"   # vortex基准（替代gzip）
  [data3]="$BENCHMARK_BZIP2"    # bzip2基准
)
EXECUTION_SEQUENCE=(data1 data2 data3)

echo "=== 双模式测试运行器: 标准模式 => ${OUTPUT_DIR_STANDARD} ; Victim Cache模式(4块) => ${OUTPUT_DIR_VICTIM} ==="
for benchmark_key in "${EXECUTION_SEQUENCE[@]}"; do echo " - ${benchmark_key}: ${BENCHMARK_SET[$benchmark_key]}"; done
echo ""

# ====== 完整测试套件执行函数（支持断点续跑）======
perform_full_benchmark_suite() {
  local target_dir="$1" vc_enabled="$2"

  # 基准配置测试
  for benchmark_key in "${EXECUTION_SEQUENCE[@]}"; do
    local output_log="${target_dir}/baseline/${benchmark_key}-baseline.log"
    execute_single_test "baseline(L2=256KB,8路,64B)" 256 8 64 "$benchmark_key" "${BENCHMARK_SET[$benchmark_key]}" "$output_log" "$vc_enabled" || true
  done

  # 容量扫描：64/128/256/512/1024 KB（相联度=8, 块大小=64）
  for capacity in 64 128 256 512 1024; do
    for benchmark_key in "${EXECUTION_SEQUENCE[@]}"; do
      local output_log="${target_dir}/cap/${benchmark_key}-cap-${capacity}.log"
      execute_single_test "容量扫描(相联度=8,块大小=64B)" "$capacity" 8 64 "$benchmark_key" "${BENCHMARK_SET[$benchmark_key]}" "$output_log" "$vc_enabled" || true
    done
  done

  # 相联度扫描：2/4/8/16/64路（容量=512KB, 块大小=64）
  for associativity in 2 4 8 16 64; do
    for benchmark_key in "${EXECUTION_SEQUENCE[@]}"; do
      local output_log="${target_dir}/way/${benchmark_key}-way-${associativity}.log"
      execute_single_test "相联度扫描(容量=512KB,块大小=64B)" 512 "$associativity" 64 "$benchmark_key" "${BENCHMARK_SET[$benchmark_key]}" "$output_log" "$vc_enabled" || true
    done
  done

  # 块大小扫描：64/128/256/512 B（容量=512KB, 相联度=8）
  for block_sz in 64 128 256 512; do
    for benchmark_key in "${EXECUTION_SEQUENCE[@]}"; do
      local output_log="${target_dir}/blk/${benchmark_key}-blk-${block_sz}.log"
      execute_single_test "块大小扫描(容量=512KB,相联度=8)" 512 8 "$block_sz" "$benchmark_key" "${BENCHMARK_SET[$benchmark_key]}" "$output_log" "$vc_enabled" || true
    done
  done
}

# ====== 执行两种模式的完整测试 ======
perform_full_benchmark_suite "${OUTPUT_DIR_STANDARD}" "off"
perform_full_benchmark_suite "${OUTPUT_DIR_VICTIM}"   "on"

echo ""
echo "=== 所有测试已完成 ==="
echo "标准模式测试结果位于: ${OUTPUT_DIR_STANDARD}/"
echo "Victim Cache模式(默认4块)测试结果位于: ${OUTPUT_DIR_VICTIM}/"
echo "子目录说明：baseline/ (基准配置) cap/ (容量扫描) way/ (相联度扫描) blk/ (块大小扫描)"
echo "日志文件命名格式示例: data1-way-8.log, data2-cap-256.log 等"


################################################################################
# 结果数据提取脚本部分：
################################################################################

#!/usr/bin/env bash
# extract_cache_results.sh - 性能数据提取工具
# 功能：从 all_sim/ 和 all_sim_victim/ 目录中的日志文件提取性能指标
# 输出：生成两个TSV格式文件 no_vc.txt 和 vc.txt
# 数据一致性：两份输出采用相同的列结构（包含L1D指标和有效L2访问缺失数）
# 指标计算规则：
#   Victim Cache启用时: eff_L1D_misses_to_L2 = dl1.vc_misses
#   Victim Cache关闭时: eff_L1D_misses_to_L2 = dl1.misses

set -euo pipefail

RESULT_FILE_STANDARD="no_vc.txt"
RESULT_FILE_VICTIM="vc.txt"

check_log_validity() {
  local log_path="$1"
  [[ -s "$log_path" ]] \
    && grep -q "^sim: \\*\\* simulation statistics \\*\\*" "$log_path" \
    && tac "$log_path" | grep -m1 -q "^  ul2\\.misses "
}

get_benchmark_abbreviation() {
  case "$1" in
    *mcf00.peak.ev6)    echo "mcf" ;;
    *vortex00.peak.ev6) echo "vortex" ;;
    *bzip200.peak.ev6)  echo "bzip2" ;;
    *)                  echo "$1" ;;
  esac
}

extract_log_metrics() {
  local log_file="$1"

  # 解析头部：测试类别 / 基准程序 / VC状态 / L2缓存配置
  local header_line test_section benchmark_executable benchmark_name vc_mode l2_config cache_sets block_bytes assoc_ways capacity_kilobytes
  header_line="$(grep -m1 "测试类别=" "$log_file" || true)"
  test_section="$(sed -n 's/.*测试类别=\(.*\)  基准程序=.*/\1/p' <<<"$header_line")"

  benchmark_executable="$(sed -n 's/.*基准程序=\(.*\)/\1/p' <<<"$header_line" | awk '{print $1}')"
  benchmark_name="$(get_benchmark_abbreviation "${benchmark_executable:-UNKNOWN}")"

  vc_mode="$(grep -m1 "^\[配置\] Victim Cache=" "$log_file" | awk -F'=| ' '{print $3}' || true)"

  # 解析 [配置] L2缓存: ul2:<sets>:<block>:<assoc>:l
  l2_config="$(grep -m1 "^\[配置\] L2缓存:" "$log_file" | sed -n 's/.*ul2:\([0-9]\+\):\([0-9]\+\):\([0-9]\+\):.*/\1 \2 \3/p')"
  cache_sets="$(awk '{print $1}' <<<"${l2_config:-0 64 1}")"
  block_bytes="$(awk   '{print $2}' <<<"${l2_config:-0 64 1}")"
  assoc_ways="$(awk '{print $3}' <<<"${l2_config:-0 64 1}")"
  if [[ -n "${cache_sets}" && -n "${block_bytes}" && -n "${assoc_ways}" && "${cache_sets}" != "0" ]]; then
    capacity_kilobytes=$(( cache_sets * block_bytes * assoc_ways / 1024 ))
  else
    capacity_kilobytes=0
  fi

  # 从日志尾部反向提取性能统计数据
  local ul2_accesses ul2_misses ul2_miss_rate dl1_accesses dl1_misses dl1_vc_hits dl1_vc_misses effective_misses effective_rate
  ul2_accesses="$(tac "$log_file" | awk '/^  ul2\.accesses /{print $2; exit}')"
  ul2_misses="$(tac "$log_file" | awk '/^  ul2\.misses /{print $2; exit}')"
  ul2_miss_rate="$(tac "$log_file" | awk '/^  ul2\.miss_rate /{print $2; exit}')"

  dl1_accesses="$(tac "$log_file" | awk '/^  dl1\.accesses /{print $2; exit}')"
  dl1_misses="$(tac "$log_file" | awk '/^  dl1\.misses /{print $2; exit}')"
  dl1_vc_hits="$(tac "$log_file" | awk '/^  dl1\.vc_hits /{print $2; exit}')"
  dl1_vc_misses="$(tac "$log_file" | awk '/^  dl1\.vc_misses /{print $2; exit}')"

  # 计算实际发送到L2的L1D缺失数
  # Victim Cache启用 -> 使用 dl1.vc_misses
  # Victim Cache关闭 -> 使用 dl1.misses
  if [[ "${vc_mode:-关闭}" == "启用" ]]; then
    effective_misses="${dl1_vc_misses:-0}"
  else
    effective_misses="${dl1_misses:-0}"
  fi

  # 计算有效L1D缺失率
  if [[ -n "${dl1_accesses:-}" && "${dl1_accesses:-0}" -gt 0 ]]; then
    effective_rate=$(awk -v a="$dl1_accesses" -v m="$effective_misses" 'BEGIN{printf("%.6f", m/a)}')
  else
    effective_rate=""
  fi

  # 将提取的数据写入对应的输出文件（保持字段一致）
  if [[ "${vc_mode:-关闭}" == "启用" ]]; then
    printf "%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$log_file" "${test_section:-NA}" "${benchmark_name:-NA}" "$capacity_kilobytes" "$assoc_ways" "$block_bytes" \
      "${ul2_accesses:-}" "${ul2_misses:-}" "${ul2_miss_rate:-}" \
      "${dl1_accesses:-}" "${dl1_misses:-}" "${dl1_vc_hits:-0}" "${dl1_vc_misses:-0}" \
      "${effective_misses:-}" "${effective_rate:-}" >> "$RESULT_FILE_VICTIM"
  else
    printf "%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$log_file" "${test_section:-NA}" "${benchmark_name:-NA}" "$capacity_kilobytes" "$assoc_ways" "$block_bytes" \
      "${ul2_accesses:-}" "${ul2_misses:-}" "${ul2_miss_rate:-}" \
      "${dl1_accesses:-}" "${dl1_misses:-}" "${dl1_vc_hits:-0}" "${dl1_vc_misses:-0}" \
      "${effective_misses:-}" "${effective_rate:-}" >> "$RESULT_FILE_STANDARD"
  fi
}

main() {
  # 统一表头（两份输出一致，便于直接对比/拼接）
  local hdr="file\tsection\tbench\tL2_capKB\tL2_assoc\tL2_blkB\tul2_accesses\tul2_misses\tul2_miss_rate\tdl1_accesses\tdl1_misses\tdl1_vc_hits\tdl1_vc_misses\teff_L1D_misses_to_L2\teff_L1D_miss_rate"
  printf "%s\n" "$hdr" > "$OUT_NO_VC"
  printf "%s\n" "$hdr" > "$OUT_VC"

  # 遍历两套日志
  while IFS= read -r -d '' f; do
    if is_log_ok "$f"; then
      parse_one "$f"
    fi
  done < <(find all_sim all_sim_victim -type f -name '*.log' -print0 | sort -z)

  echo "Wrote $OUT_NO_VC and $OUT_VC"
}

main "$@"
