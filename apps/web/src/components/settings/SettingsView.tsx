'use client'

import { useState } from 'react'
import { Settings as SettingsIcon, User, Bell, Lock, Palette, Database } from 'lucide-react'

export function SettingsView() {
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'data', label: 'Data & Privacy', icon: Database },
  ]

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
            <SettingsIcon className="w-6 h-6 text-white" />
            Settings
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Sidebar */}
        <div className="w-64 border-r border-dark-border bg-dark-surface p-4">
          <div className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-ai text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-dark-bg'
                    : 'text-dark-text-secondary hover:bg-dark-hover hover:text-dark-text-primary'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-4">Profile Settings</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-dark-text-primary mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        defaultValue="Preet"
                        className="input-primary"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-dark-text-primary mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        defaultValue="preet@example.com"
                        className="input-primary"
                      />
                    </div>
                    <button className="btn-primary">
                      <span className="text-dark-bg">Save Changes</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-dark-surface rounded-ai border border-dark-border">
                    <div>
                      <p className="font-medium text-white">Email Notifications</p>
                      <p className="text-sm text-dark-text-tertiary">Receive updates via email</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5" />
                  </div>
                  <div className="flex items-center justify-between p-4 bg-dark-surface rounded-ai border border-dark-border">
                    <div>
                      <p className="font-medium text-white">Agent Activity</p>
                      <p className="text-sm text-dark-text-tertiary">Get notified of agent responses</p>
                    </div>
                    <input type="checkbox" defaultChecked className="w-5 h-5" />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Security Settings</h2>
                <p className="text-dark-text-secondary">
                  Configure your security and privacy settings here.
                </p>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Appearance</h2>
                <p className="text-dark-text-secondary">
                  Customize the look and feel of your workspace.
                </p>
              </div>
            )}

            {activeTab === 'data' && (
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">Data & Privacy</h2>
                <p className="text-dark-text-secondary">
                  Manage your data and privacy preferences.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
