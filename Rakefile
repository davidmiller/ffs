
PROJ = "ffs"


task :coverage, :python do |t, args|
  p "Running coverage check for #{PROJ}"
  args.with_defaults :python => "python"
  sh "#{args[:python]} -m pytest --cov-report term-missing --cov=ffs test" do | ok,  res |
    if not ok
      exit 1
    end
  end
end

task :test, :python do |t, args|
  p "Running unit tests for #{PROJ}"
  args.with_defaults :python => "python"
  sh "#{args[:python]} -W ignore -m pytest test" do | ok,  res |
    if not ok
      exit 1
    end
  end
end
