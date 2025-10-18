"use client"

import { useAuth } from "../contexts/AuthContext"

const Dashboard = () => {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/50">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                LinkNest
              </span>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50">
                  <span className="text-sm font-bold text-white">
                    {user?.first_name?.[0]}
                    {user?.last_name?.[0]}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className="text-xs text-slate-400">{user?.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 hover:border-red-500/50 rounded-lg font-medium transition-all duration-200 text-sm"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 px-4">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-8 mb-8 backdrop-blur-sm">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-3">
              Welcome back,{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                {user?.first_name}
              </span>
              ! 👋
            </h1>
            <p className="text-lg text-slate-300 mb-6">You're successfully logged in to your LinkNest dashboard</p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/30 rounded-full text-green-300">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Authentication Successful
            </div>
          </div>
        </div>

        {/* Profile Card */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 mb-8 shadow-xl">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-white">Your Profile</h2>
            <div className="h-14 w-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/50">
              <span className="text-lg font-bold text-white">
                {user?.first_name?.[0]}
                {user?.last_name?.[0]}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-400 mb-2">Email Address</label>
                <p className="text-lg text-white font-medium">{user?.email}</p>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-400 mb-2">Full Name</label>
                <p className="text-lg text-white font-medium">
                  {user?.first_name} {user?.last_name}
                </p>
              </div>
            </div>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-slate-400 mb-2">Member Since</label>
                <p className="text-lg text-white font-medium">
                  {user?.date_joined
                    ? new Date(user.date_joined).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    : "N/A"}
                </p>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-400 mb-2">Account Status</label>
                <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold bg-green-500/10 border border-green-500/30 text-green-300">
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Active
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 hover:border-indigo-500/50 transition-all duration-300 group cursor-pointer">
            <div className="flex items-start gap-4">
              <div className="h-12 w-12 bg-indigo-500/10 border border-indigo-500/30 rounded-lg flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <svg className="h-6 w-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">Fast & Secure</h3>
                <p className="text-sm text-slate-400">JWT authentication with automatic token refresh</p>
              </div>
            </div>
          </div>

          {/* Feature 2 */}
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300 group cursor-pointer">
            <div className="flex items-start gap-4">
              <div className="h-12 w-12 bg-purple-500/10 border border-purple-500/30 rounded-lg flex items-center justify-center group-hover:bg-purple-500/20 transition-colors">
                <svg className="h-6 w-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">Beautiful UI</h3>
                <p className="text-sm text-slate-400">Modern design with Tailwind CSS</p>
              </div>
            </div>
          </div>

          {/* Feature 3 */}
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 hover:border-pink-500/50 transition-all duration-300 group cursor-pointer">
            <div className="flex items-start gap-4">
              <div className="h-12 w-12 bg-pink-500/10 border border-pink-500/30 rounded-lg flex items-center justify-center group-hover:bg-pink-500/20 transition-colors">
                <svg className="h-6 w-6 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">User Friendly</h3>
                <p className="text-sm text-slate-400">Intuitive interface with great UX</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
