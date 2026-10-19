import { forwardRef } from 'react';

const BASE_WIDTH = 420;
const EXPORT_WIDTH = 1080;

const COLORS = {
  page: '#F4F4F6',
  header: '#232323',
  tabs: '#CBCBCB',
  white: '#FFFFFF',
  ink: '#111111',
  text: '#232323',
  muted: '#777777',
  gray: '#666666',
  lightGray: '#888888',
  darkGray: '#222222',
  border: '#EBEBEB',
  borderLight: '#F0F0F0',
  borderMid: '#DCDCDC',
  borderDark: '#DADADA',
  green: '#009100',
  greenBg: '#E6F6EC',
  detailsBg: '#F7F3F6',
  summaryBg: '#FAFAFA',
};

const FONT =
  'Roboto, "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif';

const pad = (value) => String(value).padStart(2, '0');

function parseKickoff(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function dayLabel(date) {
  const today = new Date();
  const a = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const b = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const diff = Math.round((b - a) / 86400000);
  if (diff === 0) return 'Hoje';
  if (diff === 1) return 'Ontem';
  return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}`;
}

function formatTime(date) {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function formatOdd(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return '—';
  return numeric.toFixed(2);
}

export function formatMzn(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 'MT 0,00';
  const formatted = new Intl.NumberFormat('pt-PT', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: 'always',
  })
    .format(numeric)
    .replace(/\u00A0/g, ' ');
  return `MT ${formatted}`;
}

function homeTeam(match) {
  const parts = String(match || '').split(/\s+vs\.?\s+/i);
  return (parts[0] || '').trim() || match || '';
}

/* ----------------------------- Ícones ----------------------------- */

function IconChevronLeft({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function IconClose({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function IconNewspaper({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M21 3V18C21 19.645 19.645 21 18 21H5C3.346 21 2 19.654 2 18V16H17V18C17 18.551 17.448 19 18 19C18.565 19 19 18.565 19 18V14H4V3H21ZM8 10V12H10V10H8ZM12 10V12H17V10H12ZM8 6V8H10V6H8ZM12 6V8H17V6H12Z" />
    </svg>
  );
}

function IconSearch({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
    </svg>
  );
}

function IconFilter({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M10 2C8.69839 2 7.59786 2.83875 7.18359 4H2V6H7.18359C7.59786 7.16125 8.69839 8 10 8C11.654 8 13 6.654 13 5C13 3.346 11.654 2 10 2ZM15 4V6H22V4H15ZM15 9C13.6984 9 12.5979 9.83875 12.1836 11H2V13H12.1836C12.5979 14.1613 13.6984 15 15 15C16.654 15 18 13.654 18 12C18 10.346 16.654 9 15 9ZM20 11V13H22V11H20ZM7 16C5.69839 16 4.59786 16.8387 4.18359 18H2V20H4.18359C4.59786 21.1613 5.69839 22 7 22C8.654 22 10 20.654 10 19C10 17.346 8.654 16 7 16ZM12 18V20H22V18H12Z" />
    </svg>
  );
}

function IconCircleOpen({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" />
    </svg>
  );
}

function IconCheckCircle({ size, color = '#009100' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" fill={color}>
      <path d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" />
    </svg>
  );
}

{/* Selo circular de bilhete verificado (ícone das marcas ao lado do código de reserva) */}
function IconVerifiedSeal({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={COLORS.borderDark} aria-hidden="true">
      <path d="M12 23C18.08 23 23 18.07 23 12C23 5.92 18.07 1 12 1C5.93 1 1 5.93 1 12C1 18.08 5.93 23 12 23Z" />
      <path
        d="M4.7801 12.17C4.7801 8.18 8.0101 4.95 12.0001 4.95C15.9901 4.95 19.2201 8.18 19.2201 12.17H21.2501C21.2501 12.15 21.2501 12.14 21.2501 12.12C21.2501 7.04 17.1301 2.92 12.0501 2.92C6.9701 2.92 2.8501 7.04 2.8501 12.12C2.8501 12.14 2.8501 12.15 2.8501 12.17H4.7801Z"
        fill="#FFFFFF"
      />
      <path d="M17.5401 9.61L20.4701 6.57L19.0001 4.98L16.3101 7.54L17.5401 9.61Z" />
      <path d="M21.13 5.87L15.09 12.17C15.09 12.17 15.1 16.44 11.02 14.55L12.75 13.94L13.25 12.85L13.64 10.96L20.2 4.66L21.13 5.87Z" />
      <path
        d="M14.2098 11.73L20.8698 4.39L19.5998 3.14L17.5698 4.99L15.9998 6.41L12.2598 9.8C11.4798 9.65 10.6398 9.87 10.0398 10.47C9.07982 11.43 9.07982 12.99 10.0398 13.95C10.9998 14.91 12.5598 14.91 13.5198 13.95C14.1298 13.35 14.3498 12.52 14.2098 11.73Z"
        fill="#FFFFFF"
      />
      <path d="M11.1102 12.89C10.7302 12.51 10.7302 11.9 11.1102 11.53C11.4902 11.15 12.1002 11.15 12.4702 11.53C12.8402 11.91 12.8502 12.52 12.4702 12.89C12.0902 13.27 11.4802 13.27 11.1102 12.89Z" />
    </svg>
  );
}

function IconShieldCheck({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={COLORS.borderDark} aria-hidden="true">
      <path d="M19.33 10.8102L16.83 12.9802C16.69 14.1202 16.22 15.2102 15.47 16.0902C14.25 17.4402 12.74 18.5102 11.06 19.2202C10.96 19.2702 10.86 19.2902 10.75 19.2902C10.64 19.2902 10.53 19.2702 10.43 19.2202C8.76004 18.5102 7.26004 17.4502 6.05004 16.1002C5.12004 15.0102 4.62004 13.6202 4.63004 12.1902V8.15021C4.63004 7.74021 4.95004 7.40022 5.37004 7.39021C7.18004 7.30021 8.90004 6.59021 10.24 5.38021C10.53 5.13021 10.96 5.13021 11.25 5.38021C12.21 6.25022 13.37 6.86021 14.61 7.17021L16.45 5.12021C13.27 4.69021 11.44 2.36021 11.35 2.25021C11.2 2.07021 10.98 1.97021 10.75 1.97021C10.52 1.97021 10.3 2.07021 10.15 2.25021C10.12 2.29021 7.48004 5.69021 3.04004 5.13021C2.83004 5.08021 2.61004 5.15021 2.45004 5.30022C2.28004 5.44022 2.19004 5.65021 2.19004 5.87021V12.1802C2.18004 14.2002 2.90004 16.1502 4.21004 17.6802C5.93004 19.5902 8.08004 21.0602 10.47 21.9902C10.66 22.0702 10.87 22.0702 11.06 21.9902C13.45 21.0602 15.59 19.5902 17.31 17.6802C18.62 16.1502 19.34 14.2002 19.33 12.1802V10.8102Z" />
      <path d="M21.4401 6.28L11.4501 16.26C11.2101 16.51 10.8901 16.65 10.5401 16.65C10.2001 16.65 9.87008 16.51 9.63008 16.26L5.54008 12.2C5.22008 11.88 5.09008 11.4 5.21008 10.96C5.33008 10.52 5.68008 10.17 6.12008 10.05C6.56008 9.93001 7.04008 10.06 7.36008 10.38L10.5401 13.55L19.6101 4.46C19.9301 4.14 20.4101 4.01 20.8501 4.13C21.2901 4.25 21.6401 4.59 21.7601 5.04C21.8901 5.48 21.7601 5.95 21.4401 6.28Z" />
    </svg>
  );
}

{/* Seta do select: no original é um triângulo preenchido, não um chevron traçado */}
function IconSelectCaret({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={COLORS.ink} aria-hidden="true">
      <path d="M5 8h14l-7 8z" />
    </svg>
  );
}

function IconChevronDown({ size, color = '#111111' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.5">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

/* --------------------------- Componente --------------------------- */

const SocialProofPreview = forwardRef(function SocialProofPreview(
  { ticket, scale = 1, stakeValue = 10 },
  ref
) {
  if (!ticket) return null;

  const s = (value) => Math.round(value * scale * 100) / 100;
  const b = Math.max(1, s(1));

  const legs = ticket.legs || [];

  const stake = Number(stakeValue) || 0;
  const totalOdd = Number(ticket.total_odd) || 0;
  const returnReal = stake * totalOdd;

  const firstKickoff = legs
    .map((leg) => parseKickoff(leg.kickoff))
    .filter(Boolean)
    .sort((a, c) => a - c)[0];
  const refDate = firstKickoff || new Date();

  const wonCount = legs.filter((leg) => leg.result === 'won').length;
  const lostCount = legs.length - wonCount;

  const title = 'Aposta Múltipla';

  const summaryTeams = legs.map((leg) => homeTeam(leg.match)).filter(Boolean);
  const visibleTeams = summaryTeams.slice(0, 3);
  const moreCount = summaryTeams.length - 3;

  const tabButton = (active) => ({
    flex: 1,
    background: 'none',
    border: 'none',
    padding: s(10),
    fontSize: s(16),
    fontWeight: 'bold',
    color: COLORS.text,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: s(8),
    borderRadius: s(6),
    cursor: 'pointer',
    ...(active
      ? { backgroundColor: COLORS.white, boxShadow: '0px 2px 4px rgba(0,0,0,0.08)' }
      : {}),
  });

  const iconButton = {
    backgroundColor: COLORS.white,
    border: `${b}px solid ${COLORS.borderMid}`,
    width: s(46),
    height: s(46),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: s(8),
  };

  return (
    <div
      ref={ref}
      style={{
        width: s(BASE_WIDTH),
        backgroundColor: COLORS.page,
        color: COLORS.text,
        fontFamily: FONT,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Cabeçalho */}
      <header
        style={{
          backgroundColor: COLORS.header,
          color: COLORS.white,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: s(16),
          fontSize: s(18),
          fontWeight: 'bold',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <IconChevronLeft size={s(24)} />
          <span style={{ marginLeft: s(12) }}>Minhas Apostas</span>
        </div>
        <div
          style={{
            backgroundColor: 'rgba(255,255,255,0.08)',
            borderRadius: s(8),
            width: s(36),
            height: s(36),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: COLORS.white,
          }}
        >
          <IconClose size={s(20)} />
        </div>
      </header>

      {/* Abas */}
      <div
        style={{
          display: 'flex',
          backgroundColor: COLORS.tabs,
          padding: s(3),
          margin: `${s(12)}px ${s(10)}px`,
          borderRadius: s(8),
        }}
      >
        <button type="button" style={tabButton(false)}>
          <IconNewspaper size={s(24)} />
          Apostas Abertas
        </button>
        <button type="button" style={tabButton(true)}>
          Apostas Resultadas
        </button>
      </div>

      {/* Filtros e busca */}
      <div
        style={{
          display: 'flex',
          gap: s(8),
          padding: `0 ${s(10)}px`,
          marginBottom: s(12),
        }}
      >
        <div style={{ flex: 1, position: 'relative' }}>
          <select
            style={{
              width: '100%',
              backgroundColor: COLORS.white,
              border: `${b}px solid ${COLORS.borderMid}`,
              padding: s(12),
              paddingRight: s(36),
              borderRadius: s(8),
              fontSize: s(15),
              color: COLORS.ink,
              appearance: 'none',
              height: s(46),
            }}
            defaultValue="Desporto"
          >
            <option>Desporto</option>
          </select>
          <span
            style={{
              position: 'absolute',
              right: s(12),
              top: '50%',
              transform: 'translateY(-50%)',
              pointerEvents: 'none',
            }}
          >
            <IconSelectCaret size={s(24)} />
          </span>
        </div>
        <button type="button" style={iconButton}>
          <IconSearch size={s(24)} />
        </button>
        <button type="button" style={iconButton}>
          <IconFilter size={s(20)} />
        </button>
      </div>

      {/* Cartão do bilhete */}
      <div
        style={{
          backgroundColor: COLORS.white,
          borderRadius: s(8),
          margin: `0 ${s(16)}px ${s(16)}px`,
          border: `${b}px solid ${COLORS.border}`,
          overflow: 'hidden',
          boxShadow: '0px 1px 3px rgba(0,0,0,0.02)',
        }}
      >
        {/* Cabeçalho do cartão */}
        <div
          style={{
            padding: `${s(12)}px ${s(16)}px`,
            borderBottom: `${b}px solid ${COLORS.borderLight}`,
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: s(13),
              color: COLORS.ink,
              fontWeight: 600,
              marginBottom: s(8),
            }}
          >
            <span>Ref do bilhete: {ticket.ticket_code || '—'}</span>
            <span style={{ color: COLORS.muted, fontWeight: 'normal' }}>
              {dayLabel(refDate)} | {formatTime(refDate)}
            </span>
          </div>

          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: s(13),
              color: COLORS.gray,
              borderTop: `${b}px solid ${COLORS.borderLight}`,
              paddingTop: s(8),
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: s(6),
                color: COLORS.darkGray,
                fontWeight: 500,
              }}
            >
              Código de Reserva: {ticket.reserve_code || '—'}
            </div>
            <div style={{ display: 'flex', gap: s(6) }}>
              <IconVerifiedSeal size={s(24)} />
              <IconShieldCheck size={s(24)} />
            </div>
          </div>
        </div>

        {/* Linha múltipla + expansão */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: `${s(5)}px ${s(3)}px`,
            backgroundColor: COLORS.white,
            gap: s(3),
            flexWrap: 'nowrap',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 0,
              border: `${b}px solid ${COLORS.borderDark}`,
              borderRadius: s(4),
              overflow: 'hidden',
              fontSize: s(13),
              fontWeight: 400,
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}
          >
            <span style={{ padding: `${s(6)}px ${s(4)}px`, whiteSpace: 'nowrap' }}>
              {title} (<strong style={{ color: COLORS.green }}>{legs.length}</strong>)
            </span>
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: s(3),
                padding: `${s(6)}px ${s(4)}px`,
                borderLeft: `${b}px solid ${COLORS.borderDark}`,
                fontSize: s(13),
                fontWeight: 500,
                whiteSpace: 'nowrap',
                color: COLORS.text,
              }}
            >
              <IconCircleOpen size={s(12)} />
              {lostCount}
            </span>
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: s(3),
                padding: `${s(6)}px ${s(4)}px`,
                borderLeft: `${b}px solid ${COLORS.borderDark}`,
                fontSize: s(13),
                fontWeight: 500,
                whiteSpace: 'nowrap',
                color: COLORS.green,
              }}
            >
              <IconCheckCircle size={s(14)} />
              {wonCount}
            </span>
          </div>

          <span
            style={{
              padding: `${s(6)}px ${s(4)}px`,
              borderRadius: s(4),
              backgroundColor: COLORS.detailsBg,
              fontSize: s(13),
              fontWeight: 'bold',
              color: COLORS.ink,
              display: 'flex',
              alignItems: 'center',
              gap: s(3),
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}
          >
            Visualização de detalhes
            <IconChevronDown size={s(11)} />
          </span>
        </div>

        <div
          style={{
            padding: `0 ${s(16)}px ${s(12)}px`,
            fontSize: s(13),
            color: COLORS.lightGray,
            backgroundColor: COLORS.summaryBg,
            borderBottom: `${b}px solid ${COLORS.borderLight}`,
          }}
        >
          {visibleTeams.join(' | ')}
          {moreCount > 0 ? ` + ${moreCount} Mais` : ''}
        </div>

        {/* Valores e finanças */}
        <div
          style={{
            padding: `${s(12)}px ${s(16)}px`,
            display: 'flex',
            flexDirection: 'column',
            gap: s(6),
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: s(13),
              color: '#555555',
            }}
          >
            <span>Valor da Aposta:</span>
            <span>{formatMzn(stake)}</span>
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: s(13),
              color: '#555555',
            }}
          >
            <span>Total De Probabilidades:</span>
            <strong>{formatOdd(totalOdd)}</strong>
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: s(13),
              color: '#555555',
            }}
          >
            <span>Retorno real:</span>
            <strong>{formatMzn(returnReal)}</strong>
          </div>
        </div>

        {/* Botão de resultado */}
        <div style={{ padding: `${s(12)}px ${s(16)}px` }}>
          <button
            type="button"
            style={{
              width: '100%',
              backgroundColor: COLORS.greenBg,
              color: COLORS.green,
              border: 'none',
              padding: s(10),
              borderRadius: s(6),
              fontWeight: 'bold',
              fontSize: s(14),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: s(6),
            }}
          >
            <IconCheckCircle size={s(18)} />
            Ganhos
          </button>
        </div>
      </div>
    </div>
  );
});

export { BASE_WIDTH, EXPORT_WIDTH };
export default SocialProofPreview;
