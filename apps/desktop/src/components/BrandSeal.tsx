/** 品牌标记：墨点落砚（非印章）——小尺寸可辨 */
export function BrandSeal({ size = 28 }: { size?: number }) {
  return (
    <span className="vh-seal" style={{ width: size, height: size }} aria-hidden>
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="currentColor"
        role="img"
        aria-label="墨台"
      >
        <title>墨台</title>
        {/* 墨点：略有机的水滴形 */}
        <path d="M16 3.2c3.9 4.6 7.4 8.2 7.4 12.1 0 4.2-3.3 7.5-7.4 7.5s-7.4-3.3-7.4-7.5c0-3.9 3.5-7.5 7.4-12.1Z" />
        {/* 高光一点，避免实心发闷 */}
        <circle cx="13.6" cy="11.2" r="1.35" fill="var(--paper-1)" opacity="0.55" />
        {/* 砚台／台面 */}
        <rect x="7" y="24.2" width="18" height="2.4" rx="1.1" />
        <rect x="9.2" y="26.6" width="2.2" height="1.5" rx="0.5" opacity="0.7" />
        <rect x="20.6" y="26.6" width="2.2" height="1.5" rx="0.5" opacity="0.7" />
      </svg>
    </span>
  );
}
