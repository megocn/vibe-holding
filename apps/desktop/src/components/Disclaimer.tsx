/** 产品内统一免责声明文案与展示。 */

export const DISCLAIMER_PARAS = [
  '墨台所载条目、排行快照、对比结论与方案建议，均来自公开信息与第三方权威榜的整理展示，仅供学习与选型参考，不构成任何投资、采购、合规或专业意见。',
  '榜单名次、版本节点、定价与可用性可能滞后或与官方最新状态不一致；重大决策前请自行交叉核对一手来源，并完成独立评测。',
  '墨台与所涉厂商、开源项目及榜单主办方无隶属或背书关系。因依赖本站信息作出决策而产生的任何损失，墨台及贡献者不承担责任。',
  '桌面端「凭据管家」仍为过渡实现，请勿当作生产级密码管理器使用；高价值密钥请优先使用系统钥匙串或成熟密码工具。',
] as const;

interface DisclaimerProps {
  /** 紧凑：设置页等次要位置 */
  compact?: boolean;
  id?: string;
}

export function Disclaimer({ compact, id = 'vh-disclaimer' }: DisclaimerProps) {
  return (
    <section
      className={`vh-disclaimer${compact ? ' vh-disclaimer-compact' : ''}`}
      aria-labelledby={id}
    >
      <h2 id={id} className={compact ? 'vh-text-sm' : 'vh-home-lane-title'}>
        免责声明
      </h2>
      <div className="vh-disclaimer-body">
        {DISCLAIMER_PARAS.map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
    </section>
  );
}
