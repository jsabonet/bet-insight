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
  borderSoft: '#F5F5F5',
  borderDark: '#DADADA',
  green: '#009100',
  greenDark: '#00A63F',
  greenBg: '#E6F6EC',
  detailsBg: '#F7F3F6',
  summaryBg: '#FAFAFA',
  circleGray: '#B0B0B0',
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

function IconCheckCircle({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
        fill="#009100"
      />
    </svg>
  );
}

function IconShieldCheck({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 1.5L20 5v6c0 5.25-3.5 8.9-8 11-4.5-2.1-8-5.75-8-11V5l8-3.5z"
        fill="#009100"
      />
      <path
        d="M8.5 12l2.4 2.4 4.6-4.8"
        fill="none"
        stroke="#FFFFFF"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
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
  { ticket, scale = 1, stakeUnits = 10, unitValue = 100 },
  ref
) {
  if (!ticket) return null;

  const s = (value) => Math.round(value * scale * 100) / 100;
  const b = Math.max(1, s(1));

  const legs = ticket.legs || [];

  const units = Number(stakeUnits) || 0;
  const stake = units * (Number(unitValue) || 0);
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
            <IconChevronDown size={s(16)} />
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
              <IconCheckCircle size={s(24)} />
              <IconShieldCheck size={s(18)} />
            </div>
          </div>
        </div>

        {/* Linha múltipla + expansão */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: s(8),
            backgroundColor: COLORS.white,
            gap: s(8),
            flexWrap: 'wrap',
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
              fontSize: s(15),
              fontWeight: 400,
            }}
          >
            <span style={{ padding: s(8), whiteSpace: 'nowrap' }}>
              {title} (<strong style={{ color: COLORS.green }}>{legs.length}</strong>)
            </span>
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: s(4),
                padding: s(8),
                borderLeft: `${b}px solid ${COLORS.borderDark}`,
                fontSize: s(15),
                fontWeight: 500,
                whiteSpace: 'nowrap',
                color: COLORS.muted,
              }}
            >
              <IconCircleOpen size={s(16)} />
              {lostCount}
            </span>
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: s(4),
                padding: s(8),
                borderLeft: `${b}px solid ${COLORS.borderDark}`,
                fontSize: s(15),
                fontWeight: 500,
                whiteSpace: 'nowrap',
                color: COLORS.green,
              }}
            >
              <IconCheckCircle size={s(18)} />
              {wonCount}
            </span>
          </div>

          <span
            style={{
              padding: s(8),
              borderRadius: s(4),
              backgroundColor: COLORS.detailsBg,
              fontSize: s(15),
              fontWeight: 'bold',
              color: COLORS.ink,
              display: 'flex',
              alignItems: 'center',
              gap: s(4),
            }}
          >
            Visualização de detalhes
            <IconChevronDown size={s(14)} />
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

        {/* Lista de seleções (detalhes) */}
        <div style={{ backgroundColor: COLORS.white }}>
          {legs.map((leg, index) => {
            const kickoff = parseKickoff(leg.kickoff);
            const won = leg.result === 'won';
            const pickText = String(leg.pick || leg.market_label || 'Seleção');
            const marketText = String(leg.market_label || '');
            const showMarket =
              marketText && marketText.toLowerCase() !== pickText.toLowerCase();

            return (
              <div
                key={`${leg.fixture_id}-${leg.market}-${index}`}
                style={{
                  padding: `${s(14)}px ${s(16)}px`,
                  borderBottom: `${b}px solid ${COLORS.borderSoft}`,
                  display: 'flex',
                  gap: s(12),
                  position: 'relative',
                }}
              >
                <div style={{ marginTop: s(2) }}>
                  <div
                    style={{
                      width: s(18),
                      height: s(18),
                      borderRadius: '50%',
                      border: `${Math.max(2, s(2))}px solid ${
                        won ? COLORS.green : COLORS.circleGray
                      }`,
                      backgroundColor: won ? COLORS.green : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: COLORS.white,
                      fontSize: s(11),
                      fontWeight: 'bold',
                    }}
                  >
                    {won ? '✓' : ''}
                  </div>
                </div>

                <div style={{ flex: 1, minWidth: 0, paddingRight: s(40) }}>
                  <div
                    style={{
                      fontSize: s(13),
                      color: COLORS.lightGray,
                      marginBottom: s(2),
                    }}
                  >
                    <strong style={{ color: COLORS.darkGray }}>{pickText}</strong>
                    {showMarket ? ` | ${marketText}` : ''}
                  </div>
                  <div
                    style={{
                      fontSize: s(13),
                      fontWeight: 500,
                      color: COLORS.darkGray,
                      marginBottom: s(2),
                    }}
                  >
                    {leg.match || 'Partida'}
                  </div>
                  <div
                    style={{
                      fontSize: s(12),
                      color: COLORS.lightGray,
                      marginBottom: s(6),
                    }}
                  >
                    {[
                      leg.league,
                      kickoff ? `${dayLabel(kickoff)} ${formatTime(kickoff)}` : '',
                    ]
                      .filter(Boolean)
                      .join(' · ')}
                  </div>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: s(8),
                      fontSize: s(12),
                      color: '#555555',
                    }}
                  >
                    <span
                      style={{
                        backgroundColor: COLORS.green,
                        color: COLORS.white,
                        padding: `${s(2)}px ${s(6)}px`,
                        borderRadius: s(12),
                        fontSize: s(11),
                        fontWeight: 'bold',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: s(4),
                      }}
                    >
                      <span
                        style={{
                          width: s(6),
                          height: s(6),
                          borderRadius: '50%',
                          backgroundColor: COLORS.white,
                        }}
                      />
                      Finalizado
                    </span>
                    {leg.final_score ? <span>{String(leg.final_score)}</span> : null}
                  </div>
                </div>

                <div
                  style={{
                    position: 'absolute',
                    top: s(14),
                    right: s(16),
                    fontSize: s(14),
                    fontWeight: 'bold',
                    color: COLORS.ink,
                  }}
                >
                  {formatOdd(leg.odd)}
                </div>
              </div>
            );
          })}
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
            <strong style={{ color: COLORS.ink }}>{formatOdd(totalOdd)}</strong>
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
            <strong style={{ color: COLORS.ink }}>{formatMzn(returnReal)}</strong>
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
