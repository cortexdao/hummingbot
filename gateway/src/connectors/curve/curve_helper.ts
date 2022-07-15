import { Token, Fraction, Rounding } from '@uniswap/sdk-core';

export declare class Trade {
  executionPrice: Fraction;
  baseToken: Token;
  quoteToken: Token;
  toSignificant(
    significantDigits?: number,
    format?: Record<string, unknown>,
    rounding?: Rounding
  ): string;
}
