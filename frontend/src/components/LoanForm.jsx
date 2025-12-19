import { useState, useEffect } from 'react';
import { loansAPI, assetsAPI } from '../services/api';

const LoanForm = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    asset_id: '',
    due_date: '',
    notes: '',
  });
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingAssets, setLoadingAssets] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await assetsAPI.getAssets({ limit: 100 });
      setAssets(response.data.data.items || []);
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setLoadingAssets(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = {
        asset_id: formData.asset_id,
        due_date: formData.due_date || null,
        notes: formData.notes || null,
      };

      await loansAPI.createLoan(data);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create loan request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Asset *
        </label>
        {loadingAssets ? (
          <div className="text-slate-400">Loading assets...</div>
        ) : (
          <select
            value={formData.asset_id}
            onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
            className="input-field"
            required
          >
            <option value="">Select Asset</option>
            {assets.map((asset) => (
              <option key={asset.id} value={asset.id}>
                {asset.name} ({asset.asset_code}) - {asset.current_status}
              </option>
            ))}
          </select>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Due Date (Optional - Leave empty for open-ended loan)
        </label>
        <input
          type="datetime-local"
          value={formData.due_date}
          onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
          className="input-field"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Notes
        </label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="input-field"
          rows="3"
          placeholder="Notes for loan request..."
        />
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onClose}
          className="btn-secondary"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading || loadingAssets}
        >
          {loading ? 'Creating...' : 'Create Loan Request'}
        </button>
      </div>
    </form>
  );
};

export default LoanForm;

