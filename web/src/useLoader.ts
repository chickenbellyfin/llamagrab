import { useEffect, useRef, useState } from "react";
import { NoOp } from "./util";

/**
 * useLoader - hook which does background data loading
 * The `loader` function is called on construction.
 * Passing in refreshIntervalSecs causes loader to get called periodically, updating LoaderResult.value
 * When LoaderResult.invalidate is called, the loader is called immediately and initialLoad is set
 * to true
 */
interface LoaderResult<T> {
  value?: T
  initialLoad: boolean,
  invalidate: () => void
}

function useLoader<T>(
  loader: () => Promise<T>,
  initialValue?: T,
  refreshIntervalSecs?: number
): LoaderResult<T> {

  const [result, setResult] = useState<LoaderResult<T>>({
    value: initialValue,
    initialLoad: true,
    invalidate: NoOp
  });
  const resultRef = useRef<T>()
  const timerRef = useRef<any>(null);

  // set ref so invalidate() gets the latest result
  resultRef.current = result.value;

  const invalidate = () => {
    setResult({
      value: resultRef.current,
      initialLoad: true,
      invalidate: NoOp
    })
    clearTimeout(timerRef.current);
    runLoader();
  }

  const runLoader = async () => {
    try {
      const loaderResult = await loader()
      setResult({
        value: loaderResult,
        initialLoad: false,
        invalidate
      })
      if (refreshIntervalSecs !== undefined) {
        timerRef.current = setTimeout(runLoader, refreshIntervalSecs * 1000)
      }
    } catch (e) {
      if (refreshIntervalSecs !== undefined) {
        timerRef.current = setTimeout(runLoader, refreshIntervalSecs * 2 * 1000)
      }
    }
  }

  useEffect(() => {
    runLoader();
    return () => clearTimeout(timerRef.current);
  }, []);

  return result;
}

export default useLoader;