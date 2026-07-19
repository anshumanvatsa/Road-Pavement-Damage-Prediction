import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import Dashboard from "./pages/Dashboard";
import RoadList from "./pages/RoadList";
import RoadDetail from "./pages/RoadDetail";
import AddRoad from "./pages/AddRoad";
import DigitalTwins from "./pages/DigitalTwins";
import NotFound from "./pages/NotFound";
import { ErrorBoundary } from "./components/ErrorBoundary";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppLayout>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/roads" element={<RoadList />} />
              <Route path="/roads/:id" element={<RoadDetail />} />
              <Route path="/add-road" element={<AddRoad />} />
              <Route path="/digital-twins" element={<DigitalTwins />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </ErrorBoundary>
        </AppLayout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
