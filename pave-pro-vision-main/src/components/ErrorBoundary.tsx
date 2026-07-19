import React from 'react';

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null; errorInfo: React.ErrorInfo | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-4xl mx-auto w-full">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-500 mb-4">Application Crashed</h2>
            <p className="text-sm text-foreground mb-4">Please screenshot this page and show it to the AI:</p>
            <div className="bg-black/50 p-4 rounded overflow-auto max-h-[400px]">
              <pre className="text-xs text-red-400 mb-4">
                {this.state.error?.toString()}
              </pre>
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                {this.state.errorInfo?.componentStack}
              </pre>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
