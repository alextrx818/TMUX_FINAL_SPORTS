#!/usr/bin/env python3

"""
Odds Format Detection Test
Test different odds format interpretations against real data to determine actual format.
"""

def test_odds_formats():
    print("🧪 ODDS FORMAT DETECTION TEST")
    print("=" * 50)
    
    # Real data from our arrays
    test_cases = {
        "A25_Asian_Handicap": {
            "values": [0.97, 0.25, 0.82],  # [home_odds, handicap, away_odds]
            "description": "Asian Handicap +0.25"
        },
        "A26_MoneyLine": {
            "values": [2.3, 2.75, 3.4],  # [home_odds, draw_odds, away_odds]
            "description": "European 1X2"
        },
        "A27_OverUnder": {
            "values": [0.92, 1.75, 0.87],  # [over_odds, line, under_odds]
            "description": "Over/Under 1.75 goals"
        },
        "A28_Corners": {
            "values": [1.1, 8.5, 0.66],  # [over_odds, line, under_odds]
            "description": "Corners 8.5 total"
        }
    }
    
    def calculate_european_decimal(odds):
        """European Decimal: Total return per $1 bet"""
        return f"${odds:.2f} total return per $1 bet (${odds-1:.2f} profit)"
    
    def calculate_hong_kong(odds):
        """Hong Kong: Profit per $1 bet"""
        total_return = 1.0 + odds
        return f"${odds:.2f} profit per $1 bet (${total_return:.2f} total return)"
    
    def calculate_malaysian_positive(odds):
        """Malaysian Positive: Same as European Decimal"""
        return f"${odds:.2f} total return per $1 bet (${odds-1:.2f} profit)"
    
    def calculate_malaysian_negative(odds):
        """Malaysian Negative: Risk amount to win $1"""
        win_amount = 1.0
        total_return = odds + win_amount
        return f"Risk ${odds:.2f} to win $1.00 (${total_return:.2f} total return)"
    
    def calculate_implied_probability(odds, format_type):
        """Calculate implied probability based on format"""
        if format_type == "european":
            return (1 / odds) * 100
        elif format_type == "hong_kong":
            european_equivalent = 1.0 + odds
            return (1 / european_equivalent) * 100
        elif format_type == "malaysian_negative":
            european_equivalent = 1.0 + (1.0 / odds)
            return (1 / european_equivalent) * 100
        return 0
    
    def test_probability_sum(odds_list, format_type):
        """Test if probabilities sum to reasonable total (should be > 100% due to bookmaker margin)"""
        total_prob = sum(calculate_implied_probability(odd, format_type) for odd in odds_list if odd > 0)
        return total_prob
    
    print("\n📊 TESTING EACH MARKET:")
    
    for market, data in test_cases.items():
        print(f"\n🎯 {market}: {data['description']}")
        print(f"Raw values: {data['values']}")
        
        # Skip line values (handicap, totals) - only test betting odds
        if market == "A25_Asian_Handicap":
            betting_odds = [data['values'][0], data['values'][2]]  # Skip handicap [1]
            print(f"Testing odds: {betting_odds}")
        elif market == "A26_MoneyLine":
            betting_odds = data['values']  # All are betting odds
            print(f"Testing odds: {betting_odds}")
        elif market in ["A27_OverUnder", "A28_Corners"]:
            betting_odds = [data['values'][0], data['values'][2]]  # Skip line [1]
            print(f"Testing odds: {betting_odds}")
        
        print("\n📋 FORMAT INTERPRETATIONS:")
        
        # Test each odds value
        for i, odds in enumerate(betting_odds):
            print(f"\n  Odds value: {odds}")
            
            if odds >= 1.0:
                print(f"    European Decimal: {calculate_european_decimal(odds)}")
                print(f"    Hong Kong:        {calculate_hong_kong(odds)}")
                print(f"    Malaysian Pos:    {calculate_malaysian_positive(odds)}")
            else:
                print(f"    European Decimal: INVALID (< 1.0 impossible)")
                print(f"    Hong Kong:        {calculate_hong_kong(odds)}")
                print(f"    Malaysian Neg:    {calculate_malaysian_negative(odds)}")
        
        # Test probability sums for markets with multiple betting odds
        if len(betting_odds) > 1:
            print(f"\n  🧮 PROBABILITY TESTS:")
            
            # Test different format interpretations
            formats_to_test = []
            if all(odd >= 1.0 for odd in betting_odds):
                formats_to_test = [("european", "European Decimal"), ("hong_kong", "Hong Kong")]
            else:
                formats_to_test = [("hong_kong", "Hong Kong"), ("malaysian_negative", "Malaysian Negative")]
            
            for format_type, format_name in formats_to_test:
                prob_sum = test_probability_sum(betting_odds, format_type)
                validity = "✅ VALID" if 100 < prob_sum < 120 else "❌ INVALID"
                print(f"    {format_name}: {prob_sum:.1f}% total {validity}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS SUMMARY:")
    print("- Probability sums between 100-120% indicate valid odds format")
    print("- Values < 1.0 cannot be European Decimal")
    print("- Asian markets often use Hong Kong or Malaysian formats")
    print("- European markets typically use European Decimal format")

if __name__ == "__main__":
    test_odds_formats()