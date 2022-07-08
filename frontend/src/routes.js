import {Navigate, useRoutes} from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
import NotFound from './pages/Page404';
import TokenList from './pages/TokenList'
import TokenDetail from "./pages/TokenDetail";
/*
import DashboardApp from './pages/unused/DashboardApp';
import User from './pages/unused/User';
 */


// ----------------------------------------------------------------------

export default function Router() {
  return useRoutes([
    {
      path: '/dashboard',
      element: <DashboardLayout />,
      children: [
        { path: 'token-list', element: <TokenList /> },
        { path: 'token-list/:id', element: <TokenDetail /> },
        /* Later: User Extension
        { path: 'products', element: <Products /> },
        { path: 'blog', element: <Blog /> },
      */
      ],
    },
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard/token-list" /> },
        /*
        { path: 'login', element: <Login /> },
        { path: 'register', element: <Register /> },
        */
        { path: '404', element: <NotFound /> },
        { path: '*', element: <Navigate to="/404" /> },
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
