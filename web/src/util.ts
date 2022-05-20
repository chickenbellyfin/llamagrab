import { ScreenMap } from "antd/lib/_util/responsiveObserve";

export const NoOp = () => {};

export function getBreakpoint(breakpoint: ScreenMap): string {
    var b = 'xs';
    b = breakpoint.sm ? 'sm': b;
    b = breakpoint.md ? 'md': b;
    b = breakpoint.lg ? 'lg': b;
    b = breakpoint.xl ? 'xl': b;
    b = breakpoint.xxl ? 'xxl': b;
    return b;
}