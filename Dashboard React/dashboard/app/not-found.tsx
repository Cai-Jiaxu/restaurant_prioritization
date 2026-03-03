import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50 gap-4">
      <div className="text-center space-y-3">
        <div className="text-6xl font-bold text-primary-500">404</div>
        <h1 className="text-xl font-semibold">Page not found</h1>
        <p className="text-slate-400 text-sm">The page you're looking for doesn't exist.</p>
        <Link
          href="/"
          className="inline-block mt-4 px-5 py-2 bg-primary-500 text-slate-950 font-semibold rounded-lg hover:bg-primary-400 transition-colors text-sm"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
