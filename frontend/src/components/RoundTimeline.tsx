interface RoundTimelineProps {
  currentRound: number;
  maxRounds: number;
}

export function RoundTimeline({ currentRound, maxRounds }: RoundTimelineProps) {
  const percentage = Math.min((currentRound / maxRounds) * 100, 100);
  const dots = Array.from({ length: maxRounds }, (_, i) => i + 1);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm px-5 py-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-gray-700">Round Progress</span>
          <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
            {currentRound} / {maxRounds}
          </span>
        </div>
        <span className="text-xs text-gray-400">{Math.round(percentage)}% complete</span>
      </div>

      {/* Dot-step track — shows individual round steps up to 15, bar beyond */}
      {maxRounds <= 15 ? (
        <div className="flex items-center gap-1">
          {dots.map((round) => {
            const isDone = round < currentRound;
            const isCurrent = round === currentRound;
            return (
              <div key={round} className="flex items-center flex-1">
                <div
                  className={`h-5 w-full rounded flex items-center justify-center text-[9px] font-bold transition-all duration-300 ${
                    isDone
                      ? 'bg-blue-600 text-white'
                      : isCurrent
                      ? 'bg-indigo-500 text-white ring-2 ring-indigo-300 scale-110'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {round}
                </div>
                {round < maxRounds && (
                  <div
                    className={`h-0.5 w-1 shrink-0 ${isDone ? 'bg-blue-600' : 'bg-gray-200'}`}
                  />
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="w-full bg-gray-100 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
    </div>
  );
}
