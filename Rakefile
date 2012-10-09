
PROJ = "ffs"


task :test, :python do |t, args|
  p "Running unit tests for #{PROJ}"
  args.with_defaults :python => "python"
  sh "#{args[:python]} -W ignore -m pytest test"
end

