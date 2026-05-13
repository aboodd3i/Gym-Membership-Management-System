import { useEffect, useState } from 'react';
import { getEquipment, getMaintenanceAlerts, updateEquipmentCondition, repairEquipment } from '../api/gymApi';

function Equipment() {
  const [equipment, setEquipment] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const equipRes = await getEquipment();
        setEquipment(equipRes.data);
        
        const alertRes = await getMaintenanceAlerts();
        setAlerts(alertRes.data);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching equipment", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Mark equipment as broken
  const handleMarkBroken = async (equipId) => {
    try {
      // FIX: Send 'Broken' with a capital B to satisfy the PostgreSQL CHECK constraint
      await updateEquipmentCondition(equipId, { condition_status: 'broken' });
      alert("Equipment marked as broken! ⚠️");
      refreshData();
    } catch (error) {
      alert("Failed to update equipment.");
    }
  };

  // Mark equipment as repaired
  const handleRepaired = async (equipId) => {
    try {
      await repairEquipment(equipId);
      alert("Equipment repaired and next maintenance scheduled! ✅");
      refreshData();
    } catch (error) {
      alert("Failed to update equipment.");
    }
  };

  // Helper function to refresh data after an update
  const refreshData = async () => {
    const equipRes = await getEquipment();
    setEquipment(equipRes.data);
    const alertRes = await getMaintenanceAlerts();
    setAlerts(alertRes.data);
  };

  if (loading) return <div className="container mt-4"><h3>Loading Equipment...</h3></div>;

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Equipment Management</h2>

      {/* MAINTENANCE ALERTS SECTION */}
      {alerts.length > 0 && (
        <div className="mb-4">
          <h4 className="text-danger">⚠️ Maintenance Alerts ({alerts.length})</h4>
          <div className="row">
            {alerts.map(alert => (
              <div className="col-md-4 mb-3" key={alert.name}>
                <div className="card border-danger h-100">
                  <div className="card-body">
                    <h5 className="card-title">{alert.name}</h5>
                    <h6 className="card-subtitle mb-2 text-muted">{alert.category}</h6>
                    <p className="card-text">
                      Status: <span className="badge bg-danger">{alert.condition_status}</span>
                    </p>
                    {alert.days_until_maintenance !== null && (
                      <p className="card-text text-warning fw-bold">
                        Maintenance in {alert.days_until_maintenance} days
                      </p>
                    )}
                    <button 
                      className="btn btn-sm btn-success mt-2"
                      onClick={() => handleRepaired(alert.equipment_id)}
                    >
                      Mark Repaired
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FULL INVENTORY TABLE */}
      <h4>Full Inventory</h4>
      <table className="table table-striped table-hover shadow-sm">
        <thead className="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Category</th>
            <th>Condition</th>
            <th>Next Maintenance</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {equipment.map(item => {
            // FIX: Convert status to lowercase for consistent color checking
            const status = item.condition_status ? item.condition_status.toLowerCase() : '';
            let badgeColor = 'danger'; // default red
            if (status === 'good') badgeColor = 'success'; // Green
            else if (status.includes('repair')) badgeColor = 'warning'; // Orange/Yellow for "needs repair"
            
            return (
              <tr key={item.equipment_id}>
                <td>{item.equipment_id}</td>
                <td>{item.name}</td>
                <td>{item.category}</td>
                <td>
                  <span className={`badge bg-${badgeColor}`}>
                    {item.condition_status}
                  </span>
                </td>
                <td>{item.next_maintenance_date ? new Date(item.next_maintenance_date).toLocaleDateString() : 'N/A'}</td>
                <td>
                  {status !== 'good' ? (
                    <button className="btn btn-sm btn-outline-success" onClick={() => handleRepaired(item.equipment_id)}>
                      Repaired
                    </button>
                  ) : (
                    <button className="btn btn-sm btn-outline-danger" onClick={() => handleMarkBroken(item.equipment_id)}>
                      Report Broken
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default Equipment;