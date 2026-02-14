import { GradientSpinner } from "./gradient-spinner";

export function PageLoader() {
  return (
    <div className="flex h-full min-h-[50vh] items-center justify-center">
      <GradientSpinner size={48} />
    </div>
  );
}
