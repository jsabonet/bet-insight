import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Gift } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import Logo from '../components/Logo';
import AffiliateLinkCard from '../components/affiliate/AffiliateLinkCard';
import BalanceCard from '../components/affiliate/BalanceCard';
import AffiliateStatsCard from '../components/affiliate/AffiliateStatsCard';
import CommissionsList from '../components/affiliate/CommissionsList';
import WithdrawModal from '../components/affiliate/WithdrawModal';
import { affiliateAPI } from '../services/api';

export default function AffiliateDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [notAffiliate, setNotAffiliate] = useState(false);
  const [affiliate, setAffiliate] = useState(null);
  const [stats, setStats] = useState(null);
  const [commissions, setCommissions] = useState([]);
  const [showWithdraw, setShowWithdraw] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [meRes, statsRes, commissionsRes] = await Promise.all([
        affiliateAPI.getMe(),
        affiliateAPI.getStats(),
        affiliateAPI.getCommissions(),
      ]);
      setAffiliate(meRes.data);
      setStats(statsRes.data);
      setCommissions(commissionsRes.data);
      setNotAffiliate(false);
    } catch (err) {
      if (err.response?.status === 404) {
        setNotAffiliate(true);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Logo variant="thinking" size="xl" showText={false} />
      </div>
    );
  }

  if (notAffiliate) {
    return (
      <div className="page-container">
        <Header title="Programa de Afiliados" subtitle="Ganhe comissões ao indicar" />
        <div className="page-content">
          <div className="card animate-slide-up text-center py-10">
            <Gift className="w-16 h-16 text-primary-600 dark:text-primary-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Ainda não é afiliado
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Crie a sua conta de afiliado e comece a ganhar até 50% de comissão por cada venda.
            </p>
            <Link
              to="/affiliate/apply"
              className="inline-block px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold shadow-lg transition-all"
            >
              Tornar-me Afiliado
            </Link>
          </div>
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Afiliados" subtitle="Acompanhe os seus ganhos" />

      <div className="page-content">
        <div className="space-y-4">
          <BalanceCard
            available={affiliate?.available_balance}
            pending={affiliate?.pending_balance}
            onWithdraw={() => setShowWithdraw(true)}
          />
          <AffiliateLinkCard referralLink={affiliate?.referral_link} code={affiliate?.code} />
          <AffiliateStatsCard stats={stats} />
          <CommissionsList commissions={commissions} />
        </div>
      </div>

      {showWithdraw && (
        <WithdrawModal
          availableBalance={affiliate?.available_balance}
          onClose={() => setShowWithdraw(false)}
          onDone={() => { setShowWithdraw(false); load(); }}
        />
      )}

      <BottomNav />
    </div>
  );
}
