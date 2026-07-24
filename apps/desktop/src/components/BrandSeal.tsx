/** 朱文方印：竖排「墨台」（设计规范 §3） */
export function BrandSeal({ size = 28 }: { size?: number }) {
  const pad = 3;
  const s = size - pad * 2;
  return (
    <span className="vh-seal" style={{ width: size, height: size }} aria-hidden>
      <svg
        width={s}
        height={s}
        viewBox="0 0 32 32"
        fill="currentColor"
        role="img"
        aria-label="墨台"
      >
        <title>墨台</title>
        {/* 米字格（淡） */}
        <g opacity="0.22" stroke="currentColor" strokeWidth="0.6" fill="none">
          <line x1="16" y1="3" x2="16" y2="29" />
          <line x1="3" y1="16" x2="29" y2="16" />
          <line x1="5.5" y1="5.5" x2="26.5" y2="26.5" />
          <line x1="26.5" y1="5.5" x2="5.5" y2="26.5" />
        </g>
        <text
          x="16"
          y="14.2"
          textAnchor="middle"
          style={{
            fontFamily: 'var(--font-display), "LXGW ZhenKai", "LXGW WenKai", serif',
            fontSize: 12.5,
            fontWeight: 500,
          }}
        >
          墨
        </text>
        <text
          x="16"
          y="26.8"
          textAnchor="middle"
          style={{
            fontFamily: 'var(--font-display), "LXGW ZhenKai", "LXGW WenKai", serif',
            fontSize: 12.5,
            fontWeight: 500,
          }}
        >
          台
        </text>
      </svg>
    </span>
  );
}
