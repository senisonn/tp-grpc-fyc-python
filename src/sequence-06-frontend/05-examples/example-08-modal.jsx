// Modal
import React, { useState } from 'react';

export default function UserModal({ userId, onClose }) {
  if (!userId) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button onClick={onClose}>×</button>
        <UserDetail userId={userId} />
      </div>
    </div>
  );
}
