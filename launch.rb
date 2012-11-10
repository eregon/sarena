# python3 super_player.py -p 8000
# python3 random_player.py -p 7000
# python3 game.py -v --headless http://localhost:8000 http://localhost:7000

n = (ARGV[0] || 10).to_i

BOARD = " --board b1.dmp"

$stdout.sync = true

mean = -> sample {
  sample.reduce(0, :+) / sample.size.to_f
}

median = -> sample {
  sorted = sample.sort
  size = sample.size
  if size.odd?
    sorted[size/2]
  else
    (sorted[size/2-1] + sorted[size/2]) / 2.0
  end
}

# median absolute deviation
mad = -> sample {
  med = median[sample]
  median[sample.map { |x| (x-med).abs }]
}

begin
  player1 = spawn('python3 super_player.py  -p 8000', out: File::NULL, err: File::NULL)
  #player2 = spawn('python3 random_player.py -p 7000', out: File::NULL, err: File::NULL)
  player2 = spawn('python3 fast_player.py   -p 7000', out: File::NULL, err: File::NULL)
  sleep 0.1 # let them start

  scores = []
  steps = []
  times = []
  lines = []

  puts
  puts Time.now
  puts "Game i: score steps time"
  IO.popen("python3 game.py -v#{BOARD} -n #{n} --headless http://localhost:8000 http://localhost:7000 2>&1") do |io|
    i = 0
    while line = io.gets
      lines << line
      case line
      when /-- INFO: Starting Game (\d+)/
        print "Game #{"%2d" % Integer($1)}: "
        score = nil
        time = 0
        step = nil
      when /-- INFO: End of Game (\d+)/
        raise "Missing score line!" if !score
        times << time
        steps << step
        print "#{'%2d' % step} "
        puts "#{'%.3f' % time}s"
      when /-- INFO: Score: (-?\d+)/
        score = Integer($1)
        scores << score
        print "#{'%2d' % score} "
      when /-- INFO: Step (\d+): received action .+? in (\d+\.\d+)s/
        step = Integer($1)
        if Integer($1).odd? # player 1
          time += Float($2)
        end
      end
      puts line if $VERBOSE
    end
  end

  { score: scores, steps: steps, time: times }.each_pair { |label, sample|
    puts
    puts "#{label.capitalize}:"
    puts "Range:  [#{"%6.3f" % sample.min} - #{"%6.3f" % sample.max}] (#{"%6.3f" % (sample.max-sample.min)})"
    puts "Average: #{"%6.3f" % mean[sample]}"
    puts "Median:  #{"%6.3f" % median[sample]}"
    puts "MAD:     #{"%6.3f" % mad[sample]} (#{"%5.2f" % (mad[sample].to_f / median[sample] * 100)}%)"
  }
rescue
  p $!
  puts
  puts lines
ensure
  Process.kill('SIGTERM', player1)
  Process.kill('SIGTERM', player2)
end
