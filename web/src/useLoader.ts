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
  initialLoad: boolean
  // invalidate - fetch new values without removing old ones
  invalidate: () => void
  // reset - delete current values first, then fetch new values
  // this is useful for showing a loader during fetch
  reset: () => void
}

function useLoader<T>(
  loader: () => Promise<T>,
  initialValue?: T,
  refreshIntervalSecs?: number
): LoaderResult<T> {

  const [result, setResult] = useState<LoaderResult<T>>({
    value: initialValue,
    initialLoad: true,
    invalidate: NoOp,
    reset: NoOp,
  });
  const resultRef = useRef<T>()
  const timerRef = useRef<any>(null);

  // set ref so invalidate() gets the latest result
  resultRef.current = result.value;


  const invalidate = (reset: boolean) => {
    setResult({
      value: reset ? undefined : resultRef.current,
      initialLoad: true,
      invalidate: NoOp,
      reset: NoOp
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
        invalidate: () => invalidate(false),
        reset: () => invalidate(true)
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