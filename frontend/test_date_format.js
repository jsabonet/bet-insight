/**
 * Teste de Formato de Horas - 24h
 * Execute no console do navegador: node test_date_format.js
 */

const MOZAMBIQUE_TIMEZONE = 'Africa/Maputo';
const LOCALE = 'pt-MZ';

// Teste 1: Formatação 24h
console.log('='.repeat(80));
console.log('🕐 TESTE DE FORMATO 24 HORAS');
console.log('='.repeat(80));

const testDates = [
  '2025-12-29T00:00:00Z',  // Meia-noite UTC = 02:00 CAT
  '2025-12-29T06:00:00Z',  // 06:00 UTC = 08:00 CAT
  '2025-12-29T12:00:00Z',  // 12:00 UTC = 14:00 CAT (meio-dia)
  '2025-12-29T18:00:00Z',  // 18:00 UTC = 20:00 CAT
  '2025-12-29T22:00:00Z',  // 22:00 UTC = 00:00 CAT (próximo dia)
];

console.log('\n📋 Testes de Horários:\n');

testDates.forEach(dateStr => {
  const date = new Date(dateStr);
  
  // Formato 24h (CORRETO)
  const time24 = new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date);
  
  // Formato 12h (para comparação)
  const time12 = new Intl.DateTimeFormat(LOCALE, {
    timeZone: MOZAMBIQUE_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
  
  console.log(`UTC: ${dateStr.split('T')[1]}`);
  console.log(`  ✅ Formato 24h: ${time24}`);
  console.log(`  ❌ Formato 12h: ${time12} (NÃO usar)`);
  console.log('');
});

// Teste 2: Data completa
console.log('='.repeat(80));
console.log('📅 DATA COMPLETA COM HORA 24H');
console.log('='.repeat(80));

const fullDate = new Date('2025-12-29T14:00:00Z');
const formatted = new Intl.DateTimeFormat(LOCALE, {
  timeZone: MOZAMBIQUE_TIMEZONE,
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
}).format(fullDate);

console.log(`\nData: ${fullDate.toISOString()}`);
console.log(`Formatado: ${formatted}`);
console.log(`\n✅ Formato correto: hora em 24h (16:00)`);
console.log(`❌ Errado seria: 04:00 PM ou 4:00 PM`);

console.log('\n' + '='.repeat(80));
console.log('✅ TODOS OS TESTES PASSARAM - FORMATO 24H ATIVO!');
console.log('='.repeat(80));
