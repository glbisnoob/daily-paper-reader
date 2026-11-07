<div class="dpr-home-notice-card dpr-home-panel">
  <div class="dpr-home-notice-header dpr-home-panel-header">
    <h3 class="dpr-home-notice-title">公告与更新</h3>
    <a class="dpr-home-notice-tutorial" href="#/tutorial/README">使用教程 <span aria-hidden="true">›</span></a>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-10-05">10.05</time>
    <div>
      <strong class="dpr-home-notice-entry-title">medRxiv 自动更新已恢复</strong>
      <span class="dpr-home-notice-entry-summary">修复超长摘要导致的向量生成失败，维护任务现会限制单条 embedding 文本长度并分片写入。受影响范围已重新同步，公开读取、关键词检索与语义检索均已验证。</span>
    </div>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-09-16">09.16</time>
    <div>
      <strong class="dpr-home-notice-entry-title">日报跨日重复推荐已修复</strong>
      <span class="dpr-home-notice-entry-summary">历史推荐现按原始召回标签与 arXiv 论文标识去重，暂停词条不再参与评分；同一专题次日不会重复推荐相同论文。已有历史页面保留，不自动删除。</span>
    </div>
  </div>
  <div class="dpr-home-notice-entry">
    <time class="dpr-home-notice-date" datetime="2026-09-09">09.09</time>
    <div>
      <strong class="dpr-home-notice-entry-title">90天/365天 arXiv 专题回溯</strong>
      <span class="dpr-home-notice-entry-summary">支持分片召回、断点评审与分页查看，核心论文与待复核结果分开展示。DeepSeek 费用按实际用量计算，不下载全量 PDF。</span>
    </div>
  </div>
  <div class="dpr-home-site-stats" data-dpr-site-stats hidden aria-live="polite">
    <span>今天有 <strong class="dpr-home-site-stat-value" data-dpr-daily-readers>--</strong> 人在看论文</span>
    <span class="dpr-home-site-stat-separator" aria-hidden="true">·</span>
    <span>昨天有 <strong class="dpr-home-site-stat-value" data-dpr-yesterday-readers>--</strong> 人在看论文</span>
    <span class="dpr-home-site-stat-separator" aria-hidden="true">·</span>
    <span>已有 <strong class="dpr-home-site-stat-value" data-dpr-fork-count>--</strong> 人加入 Daily Paper Reader</span>
    <span class="dpr-home-history">
      <button type="button" class="dpr-home-history-trigger" data-dpr-history-trigger aria-label="查看最近 14 天阅读趋势"><span aria-hidden="true">🔍</span></button>
      <span class="dpr-home-history-popover" data-dpr-history-popover role="tooltip">
        <span class="dpr-home-history-header">近 14 天阅读趋势</span>
        <span class="dpr-home-history-meta">
          <span data-dpr-history-range>--</span>
          <span>峰值 <strong data-dpr-history-peak>--</strong></span>
        </span>
        <span class="dpr-home-history-chart" data-dpr-history-chart></span>
      </span>
    </span>
  </div>
</div>

<div class="dpr-home-dashboard-grid">
<section class="dpr-home-dashboard-card dpr-home-report-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">2026-10-29 ~ 2026-11-07</span>
      <h3 class="dpr-home-dashboard-title">今日汇总</h3>
    </div>
    <strong class="dpr-home-dashboard-count">共 21 篇</strong>
  </div>
  <dl class="dpr-home-dashboard-stats">
    <div class="dpr-home-dashboard-stat"><dt>累计更新</dt><dd>1 次</dd></div>
    <div class="dpr-home-dashboard-stat"><dt>精读</dt><dd>10</dd></div>
    <div class="dpr-home-dashboard-stat"><dt>速读</dt><dd>11</dd></div>
  </dl>
  <p class="dpr-home-dashboard-body">最近更新：2026-11-07 06:58:27 UTC<br>状态：成功</p>
</section>
<section class="dpr-home-dashboard-card dpr-home-brief-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">合并后生成</span>
      <h3 class="dpr-home-dashboard-title">今日简报</h3>
    </div>
    <strong class="dpr-home-dashboard-count">AI</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<p>2026-10-29至11-07共筛读21篇论文，精读10篇、速读11篇，聚焦GUI智能体与网页/电脑操作代理。</p>
<p>最值得关注的是BiGrounder以双向训练释放GUI定位潜力（10.0分），以及面向GUI智能体的高效自适应训练（9.0分）；动态目标修订、验证式探索等速读工作也值得扫一眼。</p>
<p>普通读者可先读这两篇精读的高分论文，再按“基准测试—训练效率”线索补看速读列表。</p>
  </div>
</section>
<section class="dpr-home-dashboard-card dpr-home-deep-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">今日累计</span>
      <h3 class="dpr-home-dashboard-title">精读推荐</h3>
    </div>
    <strong class="dpr-home-dashboard-count">10 篇</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<ul class="dpr-home-dashboard-paper-list"><li><span class="dpr-home-dashboard-paper-title" title="BiGrounder: Bidirectional Training Unlocks the Potential of GUI Grounding">BiGrounder: Bidirectional Training Unlocks the Potential of GUI Grounding</span></li><li><span class="dpr-home-dashboard-paper-title" title="Where to Learn and How Far to Roll Out: Efficient Adaptive Training for GUI Agents">Where to Learn and How Far to Roll Out: Efficient Adaptive Training for GUI Agents</span></li><li><span class="dpr-home-dashboard-paper-title" title="Online Dense Reinforcement Learning with Planning-Grounding Agent for UI Navigation on Live IOS Apps">Online Dense Reinforcement Learning with Planning-Grounding Agent for UI Navigation on Live IOS Apps</span></li></ul>
  </div>
  <div class="dpr-home-dashboard-tags"><span class="dpr-home-dashboard-tag">gui-agents <strong>10</strong></span></div>
</section>
<section class="dpr-home-dashboard-card dpr-home-skim-card">
  <div class="dpr-home-dashboard-header">
    <div>
      <span class="dpr-home-dashboard-kicker">今日累计</span>
      <h3 class="dpr-home-dashboard-title">速读推荐</h3>
    </div>
    <strong class="dpr-home-dashboard-count">11 篇</strong>
  </div>
  <div class="dpr-home-dashboard-body">
<ul class="dpr-home-dashboard-paper-list"><li><span class="dpr-home-dashboard-paper-title" title="DynaRev: Benchmarking Web Agents under Dynamic Goal Revision">DynaRev: Benchmarking Web Agents under Dynamic Goal Revision</span></li><li><span class="dpr-home-dashboard-paper-title" title="VeriCUA: Verification as Agentic Exploration for Computer-Using Agents">VeriCUA: Verification as Agentic Exploration for Computer-Using Agents</span></li><li><span class="dpr-home-dashboard-paper-title" title="UI-UG 2: Advancing Mobile UI Understanding and Generation with Fine-Grained Supervision and Reinforcement Learning">UI-UG 2: Advancing Mobile UI Understanding and Generation with Fine-Grained Supervision and Reinforcement Learning</span></li></ul>
  </div>
  <div class="dpr-home-dashboard-tags"><span class="dpr-home-dashboard-tag">gui-agents <strong>11</strong></span></div>
</section>
</div>

<div class="dpr-home-promo-card dpr-home-panel">
  <div class="dpr-home-panel-header">
    <h3 class="dpr-home-promo-title">社区与支持</h3>
  </div>
  <p class="dpr-home-promo-copy">欢迎通过 Star、Fork、Issue 或 PR 一起完善 Daily Paper Reader。</p>
  <div class="dpr-home-promo-meta">
    <span>QQ群 <strong>583867967</strong></span>
    <span class="dpr-home-promo-separator" aria-hidden="true">·</span>
    <span>已有 <strong>1,491</strong> 人参与交流</span>
  </div>
</div>
