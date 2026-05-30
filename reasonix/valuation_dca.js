#!/usr/bin/env node
/**
 * 📊 估值择时定投策略助手 (Valuation-Based DCA Assistant)
 * =========================================================
 * Node.js 版 — 无需任何第三方依赖，开箱即用。
 *
 * 策略规则:
 *   PE百分位 < 30%  (低估区)   → 加码  ¥1,500
 *   PE百分位 30%~70% (正常区) → 基准  ¥1,000
 *   PE百分位 > 70%  (高估区)   → 减码  ¥500
 *
 * 用法:
 *   node valuation_dca.js                     # 自动获取数据
 *   node valuation_dca.js --manual            # 手动输入
 *   node valuation_dca.js --simulate          # 回测对比
 *   node valuation_dca.js --simulate --years 10
 *   node valuation_dca.js --json              # JSON 输出
 *
 * 作者: Reasonix Code  |  免责: 仅用于研究参考，不构成投资建议。
 */

"use strict";

// ═══════════════════════════════════════════════════════════════
// 配置
// ═══════════════════════════════════════════════════════════════

const CONFIG = {
  THRESHOLD_LOW: 0.30,          // 低估线 30%
  THRESHOLD_HIGH: 0.70,         // 高估线 70%
  AMOUNT_MAP: {
    低估: 1500,
    正常: 1000,
    高估: 500,
  },
  PORTFOLIO_WEIGHTS: {
    沪深300: 0.35,
    中证500: 0.20,
    纳斯达克100: 0.25,
    红利低波: 0.20,
  },
  INITIAL_CAPITAL: 10000,
  MONTHLY_BASE: 1000,
  CASH_YIELD: 0.02,    // 闲置资金年化
};

// ═══════════════════════════════════════════════════════════════
// 工具函数
// ═══════════════════════════════════════════════════════════════

function zoneFromPercentile(pct) {
  if (pct < CONFIG.THRESHOLD_LOW * 100) return "低估";
  if (pct > CONFIG.THRESHOLD_HIGH * 100) return "高估";
  return "正常";
}

function amountFromZone(zone) {
  return CONFIG.AMOUNT_MAP[zone] ?? 1000;
}

function colorEmoji(zone) {
  return { 低估: "🟢", 正常: "🟡", 高估: "🔴" } [zone] ?? "⚪";
}

function fmt(n) {
  if (typeof n === "number") {
    if (n >= 1_000_000) return (n / 10_000).toFixed(1) + "万";
    if (n >= 10_000) return (n / 10_000).toFixed(2) + "万";
    return "¥" + n.toLocaleString("zh-CN");
  }
  return String(n);
}

function fmtPct(n) {
  return (n >= 0 ? "+" : "") + n.toFixed(1) + "%";
}

// ═══════════════════════════════════════════════════════════════
// 数据获取
// ═══════════════════════════════════════════════════════════════

async function fetchCSI300() {
  /**
   * 来源1: 蛋卷基金公开估值API
   * https://danjuanapp.com/djapi/fund/valuation-detail/SH000300
   */
  try {
    const url = "https://danjuanapp.com/djapi/fund/valuation-detail/SH000300";
    const resp = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
      signal: AbortSignal.timeout(8000),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const d = data?.data;
    if (!d?.pe_percentile) throw new Error("缺少百分位数据");

    return {
      name: "沪深300",
      currentPE: d.pe,
      percentile: d.pe_percentile,
      medianPE: d.pe_median,
      minPE5y: d.pe_min,
      maxPE5y: d.pe_max,
      source: "蛋卷基金",
      zone: zoneFromPercentile(d.pe_percentile),
    };
  } catch (err) {
    console.warn("  ⚠️ 蛋卷基金API失败:", err.message);
  }

  // 来源2: 内置缓存参考值
  return {
    name: "沪深300",
    currentPE: 12.5,
    percentile: 45.0,
    source: "内置缓存（非实时）",
    zone: "正常",
  };
}

async function fetchNasdaq100() {
  /**
   * Yahoo Finance API 获取纳指100当前PE
   * 然后用历史范围估算百分位
   */
  try {
    const url =
      "https://query1.finance.yahoo.com/v10/finance/quoteSummary/%5ENDX?modules=summaryDetail,defaultKeyStatistics";
    const resp = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
      signal: AbortSignal.timeout(8000),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const qs = data?.quoteSummary?.result?.[0];
    if (!qs) throw new Error("无法解析Yahoo数据");

    // 尝试获取PE (forwardPE > trailingPE > priceEarnings)
    let pe = null;
    for (const key of ["forwardPE", "trailingPE", "priceEarnings"]) {
      const raw =
        qs.summaryDetail?.[key]?.raw ??
        qs.defaultKeyStatistics?.[key]?.raw;
      if (raw && raw > 0) {
        pe = raw;
        break;
      }
    }
    if (!pe) throw new Error("无法获取PE");

    // 历史参考范围 (纳指100 PE通常在20~40之间)
    const histMin = 20.0,
      histMax = 40.0;
    const clamped = Math.max(histMin, Math.min(histMax, pe));
    const percentile = ((clamped - histMin) / (histMax - histMin)) * 100;

    return {
      name: "纳斯达克100",
      currentPE: pe,
      percentile: Math.round(percentile * 10) / 10,
      minPE5y: histMin,
      maxPE5y: histMax,
      source: "Yahoo Finance",
      zone: zoneFromPercentile(percentile),
    };
  } catch (err) {
    console.warn("  ⚠️ Yahoo Finance API失败:", err.message);
  }

  return {
    name: "纳斯达克100",
    currentPE: 33.0,
    percentile: 55.0,
    source: "内置缓存（非实时）",
    zone: "正常",
  };
}

function manualInput() {
  const readline = require("readline");
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    console.log("\n📝 手动输入模式");
    console.log("-".repeat(40));
    rl.question("  沪深300 PE百分位 (0~100): ", (csi) => {
      rl.question("  纳斯达克100 PE百分位 (0~100): ", (ndx) => {
        rl.close();
        const csiP = parseFloat(csi);
        const ndxP = parseFloat(ndx);
        if (
          isNaN(csiP) ||
          isNaN(ndxP) ||
          csiP < 0 ||
          csiP > 100 ||
          ndxP < 0 ||
          ndxP > 100
        ) {
          console.log("  ⚠️ 输入无效，使用默认值 50%");
          resolve([50.0, 50.0]);
        } else {
          resolve([csiP, ndxP]);
        }
      });
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// 策略核心
// ═══════════════════════════════════════════════════════════════

function decideStrategy(csi300Pct, ndxPct) {
  // 综合百分位 = 沪深300×0.55 + 纳指×0.25 + 红利低波(中性50)×0.20
  const combined = csi300Pct * 0.55 + ndxPct * 0.25 + 50.0 * 0.20;
  const zone = zoneFromPercentile(combined);
  const totalAmt = amountFromZone(zone);

  // 按组合权重分配
  const allocation = {};
  let remaining = totalAmt;
  for (const [name, weight] of Object.entries(CONFIG.PORTFOLIO_WEIGHTS)) {
    const alloc = Math.round(totalAmt * weight);
    allocation[name] = alloc;
    remaining -= alloc;
  }
  if (remaining !== 0) allocation["沪深300"] += remaining;

  return {
    combinedPercentile: Math.round(combined * 10) / 10,
    combinedZone: zone,
    totalAmount: totalAmt,
    allocation,
    detail: {
      沪深300: {
        percentile: Math.round(csi300Pct * 10) / 10,
        zone: zoneFromPercentile(csi300Pct),
        suggest: amountFromZone(zoneFromPercentile(csi300Pct)),
      },
      纳斯达克100: {
        percentile: Math.round(ndxPct * 10) / 10,
        zone: zoneFromPercentile(ndxPct),
        suggest: amountFromZone(zoneFromPercentile(ndxPct)),
      },
    },
  };
}

// ═══════════════════════════════════════════════════════════════
// 回测模拟器
// ═══════════════════════════════════════════════════════════════

const HISTORICAL_DATA = (() => {
  // 基于A股+美股真实走势特征合成的5年数据
  // (月序号, 沪深300百分位, 纳指100百分位, 沪深月收益, 纳指月收益)
  const raw = [
    // 第1年 — 底部区域逐步走出
    [1, 18, 25, 0.025, 0.015],
    [2, 15, 22, -0.010, 0.010],
    [3, 12, 20, 0.035, 0.025],
    [4, 10, 18, 0.020, 0.018],
    [5, 8, 16, 0.045, 0.030],
    [6, 11, 19, -0.015, -0.008],
    [7, 9, 17, 0.030, 0.022],
    [8, 7, 15, 0.055, 0.035],
    [9, 13, 21, -0.020, -0.010],
    [10, 10, 18, 0.040, 0.028],
    [11, 14, 22, -0.025, -0.012],
    [12, 16, 24, 0.038, 0.020],
    // 第2年 — 温和上涨
    [13, 20, 28, 0.028, 0.018],
    [14, 22, 30, 0.045, 0.025],
    [15, 25, 33, 0.032, 0.020],
    [16, 28, 35, 0.018, 0.015],
    [17, 30, 38, 0.022, 0.012],
    [18, 32, 40, 0.015, 0.010],
    [19, 35, 42, 0.020, 0.018],
    [20, 38, 45, 0.010, 0.008],
    [21, 40, 47, 0.025, 0.015],
    [22, 42, 48, 0.008, 0.010],
    [23, 45, 50, -0.012, -0.005],
    [24, 48, 52, 0.018, 0.012],
    // 第3年 — 牛市加速
    [25, 50, 55, 0.035, 0.022],
    [26, 55, 58, 0.050, 0.030],
    [27, 60, 62, 0.042, 0.025],
    [28, 65, 65, 0.038, 0.020],
    [29, 68, 68, 0.028, 0.018],
    [30, 72, 70, 0.020, 0.015],
    [31, 75, 73, 0.015, 0.010],
    [32, 78, 75, -0.008, -0.005],
    [33, 80, 78, 0.010, 0.008],
    [34, 82, 80, 0.005, 0.005],
    [35, 85, 82, -0.020, -0.010],
    [36, 88, 85, 0.008, 0.006],
    // 第4年 — 牛市见顶 → 熊市暴跌
    [37, 90, 88, 0.025, 0.015],
    [38, 92, 90, 0.018, 0.010],
    [39, 95, 92, -0.035, -0.020],
    [40, 93, 89, -0.050, -0.035],
    [41, 88, 85, -0.080, -0.055],
    [42, 82, 80, -0.060, -0.040],
    [43, 75, 73, -0.040, -0.025],
    [44, 68, 65, -0.025, -0.015],
    [45, 60, 58, -0.015, -0.008],
    [46, 52, 50, 0.010, 0.008],
    [47, 45, 42, 0.025, 0.015],
    [48, 38, 35, 0.035, 0.022],
    // 第5年 — 底部震荡 → 复苏
    [49, 32, 30, 0.020, 0.012],
    [50, 28, 26, 0.045, 0.028],
    [51, 25, 22, 0.030, 0.020],
    [52, 22, 20, 0.028, 0.018],
    [53, 20, 18, 0.035, 0.025],
    [54, 18, 16, 0.050, 0.030],
    [55, 22, 20, 0.018, 0.010],
    [56, 25, 22, 0.040, 0.025],
    [57, 28, 25, 0.032, 0.020],
    [58, 30, 28, 0.025, 0.015],
    [59, 28, 26, -0.010, -0.005],
    [60, 26, 24, 0.028, 0.018],
  ];
  return raw;
})();

function maxDrawdown(values) {
  let peak = values[0];
  let maxDd = 0;
  for (const v of values) {
    if (v > peak) peak = v;
    const dd = (peak - v) / peak;
    if (dd > maxDd) maxDd = dd;
  }
  return maxDd;
}

function runBacktest(years = 5) {
  const months = years * 12;
  const data = HISTORICAL_DATA.slice(0, months);

  // 估值择时
  let valCash = CONFIG.INITIAL_CAPITAL;
  let valNav = 1.0;
  let valShares = 0;
  let valTotalInvested = 0;

  // 固定定投
  let fixCash = CONFIG.INITIAL_CAPITAL;
  let fixNav = 1.0;
  let fixShares = 0;
  let fixTotalInvested = 0;

  const records = [];
  const valNavHistory = [];
  const fixNavHistory = [];

  for (const [m, csiPct, ndxPct, csiRet, ndxRet] of data) {
    const combinedPct = csiPct * 0.55 + ndxPct * 0.25 + 50.0 * 0.20;
    const zone = zoneFromPercentile(combinedPct);
    const investVal = amountFromZone(zone);
    const investFix = CONFIG.MONTHLY_BASE;

    // 组合月收益
    const csi500Ret = csiRet * 1.2;
    const divRet = csiRet * 0.5;
    const portRet =
      0.35 * csiRet + 0.20 * csi500Ret + 0.25 * ndxRet + 0.20 * divRet;

    // ── 估值择时 ──
    const valYield = valCash * (CONFIG.CASH_YIELD / 12);
    const actualVal = Math.min(investVal, valCash + valYield);
    valCash = valCash + valYield - actualVal;
    valNav = valNav * (1 + portRet);
    valShares += actualVal / valNav;
    valTotalInvested += actualVal;
    const valTotal = valShares * valNav + valCash;
    valNavHistory.push(valTotal);

    // ── 固定定投 ──
    const fixYield = fixCash * (CONFIG.CASH_YIELD / 12);
    const actualFix = Math.min(investFix, fixCash + fixYield);
    fixCash = fixCash + fixYield - actualFix;
    fixNav = fixNav * (1 + portRet);
    fixShares += actualFix / fixNav;
    fixTotalInvested += actualFix;
    const fixTotal = fixShares * fixNav + fixCash;
    fixNavHistory.push(fixTotal);

    records.push({
      month: m,
      csiPct,
      ndxPct,
      combinedPct: Math.round(combinedPct * 10) / 10,
      zone,
      investVal,
      portReturn: Math.round(portRet * 10000) / 100,
      valTotal: Math.round(valTotal * 100) / 100,
      fixTotal: Math.round(fixTotal * 100) / 100,
    });
  }

  // 统计
  const valFinal = valNavHistory[valNavHistory.length - 1];
  const fixFinal = fixNavHistory[fixNavHistory.length - 1];
  const valTotalIn = CONFIG.INITIAL_CAPITAL + valTotalInvested;
  const fixTotalIn = CONFIG.INITIAL_CAPITAL + fixTotalInvested;
  const yearsActual = months / 12;

  function annualRet(final, totalInvested) {
    const totalInput = CONFIG.INITIAL_CAPITAL + totalInvested;
    if (totalInput <= 0) return 0;
    const ratio = final / totalInput;
    if (ratio <= 0) return 0;
    return (Math.pow(ratio, 1 / yearsActual) - 1) * 100;
  }

  const valAnn = annualRet(valFinal, valTotalInvested);
  const fixAnn = annualRet(fixFinal, fixTotalInvested);
  const valDd = maxDrawdown(valNavHistory) * 100;
  const fixDd = maxDrawdown(fixNavHistory) * 100;

  const undervalueCount = records.filter((r) => r.zone === "低估").length;
  const overvalueCount = records.filter((r) => r.zone === "高估").length;

  return {
    params: {
      初始资金: "¥" + CONFIG.INITIAL_CAPITAL.toLocaleString("zh-CN"),
      基准月定投: "¥" + CONFIG.MONTHLY_BASE.toLocaleString("zh-CN"),
      回测周期: `${years} 年 (${months} 个月)`,
      闲置资金收益: CONFIG.CASH_YIELD * 100 + "%/年",
    },
    valuationDCA: {
      总投入: "¥" + valTotalIn.toLocaleString("zh-CN"),
      期末总资产: "¥" + Math.round(valFinal).toLocaleString("zh-CN"),
      总收益:
        "¥" +
        (valFinal - valTotalIn).toLocaleString("zh-CN", {
          signDisplay: "always",
        }),
      收益率: fmtPct(((valFinal - valTotalIn) / valTotalIn) * 100),
      年化收益率: fmtPct(valAnn),
      最大回撤: valDd.toFixed(1) + "%",
    },
    fixedDCA: {
      总投入: "¥" + fixTotalIn.toLocaleString("zh-CN"),
      期末总资产: "¥" + Math.round(fixFinal).toLocaleString("zh-CN"),
      总收益:
        "¥" +
        (fixFinal - fixTotalIn).toLocaleString("zh-CN", {
          signDisplay: "always",
        }),
      收益率: fmtPct(((fixFinal - fixTotalIn) / fixTotalIn) * 100),
      年化收益率: fmtPct(fixAnn),
      最大回撤: fixDd.toFixed(1) + "%",
    },
    comparison: {
      收益差额:
        "¥" +
        (valFinal - fixFinal).toLocaleString("zh-CN", {
          signDisplay: "always",
        }),
      年化超额收益: fmtPct(valAnn - fixAnn),
      回撤改善: fmtPct(fixDd - valDd),
      低估期买入次数: undervalueCount,
      高估期买入次数: overvalueCount,
    },
    records: records.slice(0, 60),
  };
}

// ═══════════════════════════════════════════════════════════════
// 显示函数
// ═══════════════════════════════════════════════════════════════

function showValuation(snapshot) {
  const e = colorEmoji(snapshot.zone);
  console.log(`\n  ${e} ${snapshot.name}`);
  console.log(`    当前PE: ${snapshot.currentPE?.toFixed?.(2) ?? "N/A"}`);
  console.log(`    历史百分位: ${snapshot.percentile?.toFixed?.(1)}%`);
  console.log(`    估值区间: ${snapshot.zone}`);
  console.log(`    数据来源: ${snapshot.source}`);
}

function showDecision(decision) {
  const e = colorEmoji(decision.combinedZone);
  console.log("\n" + "=".repeat(55));
  console.log("  📋 本期定投策略决策");
  console.log("=".repeat(55));

  console.log(
    `\n  📊 综合估值百分位:  ${decision.combinedPercentile}%  ${e} ${decision.combinedZone}`
  );

  const amt = decision.totalAmount;
  console.log(`\n  💰 建议定投总额:  ${fmt(amt)}`);
  if (amt > CONFIG.MONTHLY_BASE) {
    const pct = Math.round(((amt / CONFIG.MONTHLY_BASE - 1) * 100));
    console.log(`     ↑ 加码 ${pct}%（低估加仓，积累更多份额）`);
  } else if (amt < CONFIG.MONTHLY_BASE) {
    const pct = Math.round((1 - amt / CONFIG.MONTHLY_BASE) * 100);
    console.log(`     ↓ 减码 ${pct}%（高估减仓，保留现金等待回调）`);
  } else {
    console.log(`     → 维持基准定投`);
  }

  console.log(`\n  📦 资产分配:`);
  for (const [name, alloc] of Object.entries(decision.allocation)) {
    const pct = ((alloc / amt) * 100).toFixed(1);
    console.log(`    ${name.padEnd(12)}  ${fmt(alloc).padEnd(6)}  (${pct}%)`);
  }

  console.log(`\n  📈 各指数明细:`);
  for (const [name, d] of Object.entries(decision.detail)) {
    const e2 = colorEmoji(d.zone);
    console.log(
      `    ${name.padEnd(12)}  ${e2} 百分位 ${d.percentile}%  |  ` +
        `区间 ${d.zone}  | 单独建议 ${fmt(d.suggest)}`
    );
  }
  console.log("\n" + "=".repeat(55));
}

function showBacktest(result) {
  console.log("\n" + "=".repeat(60));
  console.log("  🔬 回测对比: 固定定投 vs 估值择时定投");
  console.log("=".repeat(60));

  console.log("\n  参数设置:");
  for (const [k, v] of Object.entries(result.params)) {
    console.log(`    ${k}: ${v}`);
  }

  const v = result.valuationDCA;
  const f = result.fixedDCA;
  const c = result.comparison;

  const padVal = (s) => s.padStart(14);
  console.log(`\n  ┌───────────────────────┬──────────────────┬──────────────────┐`);
  console.log(`  │ 指标                  │ 固定定投          │ 估值择时          │`);
  console.log(`  ├───────────────────────┼──────────────────┼──────────────────┤`);
  console.log(`  │ 总投入                │ ${padVal(f.总投入)} │ ${padVal(v.总投入)} │`);
  console.log(`  │ 期末总资产            │ ${padVal(f.期末总资产)} │ ${padVal(v.期末总资产)} │`);
  console.log(`  │ 总收益                │ ${padVal(f.总收益)} │ ${padVal(v.总收益)} │`);
  console.log(`  │ 总收益率              │ ${padVal(f.收益率)} │ ${padVal(v.收益率)} │`);
  console.log(`  │ 年化收益率            │ ${padVal(f.年化收益率)} │ ${padVal(v.年化收益率)} │`);
  console.log(`  │ 最大回撤              │ ${padVal(f.最大回撤)} │ ${padVal(v.最大回撤)} │`);
  console.log(`  └───────────────────────┴──────────────────┴──────────────────┘`);

  console.log(`\n  📊 对比总结:`);
  console.log(`    • 收益差额: ${c.收益差额}`);
  console.log(`    • 年化超额收益: ${c.年化超额收益}`);
  console.log(`    • 最大回撤改善: ${c.回撤改善}`);
  console.log(`    • 低估期加码次数: ${c.低估期买入次数} 次`);
  console.log(`    • 高估期减码次数: ${c.高估期买入次数} 次`);

  console.log(`\n  📈 月线走势 (每6个月):`);
  const header = `  ${"月份".padStart(5)}  ${"沪深%".padStart(5)}  ${"纳指%".padStart(5)}  ${"综合%".padStart(5)}  ` +
    `${"区间".padEnd(4)}  ${"定投".padStart(5)}  ${"估值净值".padStart(9)}  ${"固定净值".padStart(9)}`;
  console.log(header);
  for (const r of result.records) {
    if (r.month % 6 === 0 || r.month === 1) {
      console.log(
        `  ${String(r.month).padStart(5)}  ${r.csiPct.toFixed(1).padStart(5)}  ` +
          `${r.ndxPct.toFixed(1).padStart(5)}  ${r.combinedPct.toFixed(1).padStart(5)}  ` +
          `${r.zone.padEnd(4)}  ¥${r.investVal.toString().padStart(4)}  ` +
          `¥${Math.round(r.valTotal).toLocaleString("zh-CN").padStart(8)}  ` +
          `¥${Math.round(r.fixTotal).toLocaleString("zh-CN").padStart(8)}`
      );
    }
  }

  console.log("\n" + "=".repeat(60));
}

// ═══════════════════════════════════════════════════════════════
// 主入口
// ═══════════════════════════════════════════════════════════════

async function main() {
  const args = process.argv.slice(2);
  const isManual = args.includes("--manual");
  const isSimulate = args.includes("--simulate");
  const isJson = args.includes("--json");
  const yearsIdx = args.indexOf("--years");
  const years =
    yearsIdx >= 0 && yearsIdx + 1 < args.length
      ? parseInt(args[yearsIdx + 1], 10) || 5
      : 5;
  const csiArgIdx = args.indexOf("--csi");
  const ndxArgIdx = args.indexOf("--ndx");
  const argCsiPct =
    csiArgIdx >= 0 && csiArgIdx + 1 < args.length
      ? parseFloat(args[csiArgIdx + 1])
      : NaN;
  const argNdxPct =
    ndxArgIdx >= 0 && ndxArgIdx + 1 < args.length
      ? parseFloat(args[ndxArgIdx + 1])
      : NaN;

  // ── 回测模式 ──
  if (isSimulate) {
    const result = runBacktest(years);
    if (isJson) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      showBacktest(result);
    }
    return;
  }

  // ── 获取数据 ──
  let csiPct, ndxPct;

  if (isManual) {
    if (!isNaN(argCsiPct) && !isNaN(argNdxPct)) {
      csiPct = argCsiPct;
      ndxPct = argNdxPct;
      if (!isJson) {
        console.log(`\n  📌 使用命令行参数: 沪深300=${csiPct}%  纳指100=${ndxPct}%`);
      }
    } else if (process.stdin.isTTY) {
      const input = await manualInput();
      csiPct = input[0];
      ndxPct = input[1];
    } else {
      // 非交互环境，使用默认值
      csiPct = 50.0;
      ndxPct = 50.0;
      if (!isJson) {
        console.log("\n  ⚠️  非交互环境，使用默认值 50%（正常区间）");
      }
    }
  } else {
    console.log("\n📡 正在获取实时估值数据...\n");
    const csi = await fetchCSI300();
    const ndx = await fetchNasdaq100();

    if (!isJson) {
      showValuation(csi);
      showValuation(ndx);
    }

    csiPct = csi.percentile ?? 50.0;
    ndxPct = ndx.percentile ?? 50.0;
  }

  // 策略计算
  const decision = decideStrategy(csiPct, ndxPct);

  if (isJson) {
    console.log(
      JSON.stringify(
        { 沪深300: { percentile: csiPct }, 纳斯达克100: { percentile: ndxPct }, 决策: decision },
        null,
        2
      )
    );
  } else {
    showDecision(decision);

    // 建议
    const zone = decision.combinedZone;
    console.log();
    if (zone === "低估") {
      console.log(
        "  💡 当前市场整体处于 📉 低估区域，建议加大定投力度，\n" +
          "     用更低的成本积累更多份额。保持耐心，等待价值回归。"
      );
    } else if (zone === "高估") {
      console.log(
        "  💡 当前市场整体处于 📈 高估区域，建议减少定投金额，\n" +
          "     保留部分现金储备。可考虑将减省的资金放入货币基金，\n" +
          "     等待市场回调后再加大投入。"
      );
    } else {
      console.log(
        "  💡 当前市场整体处于 ⚖️ 正常估值区域，按计划执行定投。\n" +
          "     同时密切关注市场动态，为下一阶段的调整做好准备。"
      );
    }
    console.log();
  }
}

main().catch((err) => {
  console.error("❌ 发生错误:", err.message);
  process.exit(1);
});
